"""Plan and run the repository-owned, review-only AI research agent.

The planner is deterministic and credential-free. The runner calls the OpenAI
Responses API only when a post-match or pre-match task is due, then writes a
schema-validated packet outside production data directories. It never edits
observations, posteriors, manager priors, lineup projections, or deployments.
"""

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from .validate_data import REPO_ROOT, ValidationError, validate_file, validate_schema
except ImportError:  # Support direct execution.
    from validate_data import REPO_ROOT, ValidationError, validate_file, validate_schema


FIXTURES_DIR = REPO_ROOT / "data" / "fixtures"
RESEARCH_DIR = REPO_ROOT / "data" / "research_drafts"
PROJECTION_PATH = REPO_ROOT / "data" / "lineup_projection" / "iraola_2026_27.json"
PRIOR_PATH = REPO_ROOT / "data" / "manager_priors" / "iraola_2026.json"
SQUAD_PATH = REPO_ROOT / "data" / "squad" / "liverpool_2026_27.json"
PLAYER_PROFILES_DIR = REPO_ROOT / "data" / "player_profiles"
PROMPT_PATH = REPO_ROOT / "prompts" / "research_agent.md"
PACKET_SCHEMA_PATH = REPO_ROOT / "schema" / "agent_research_packet.schema.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "research_agent"
TERMINAL_STATUSES = {"FINISHED", "AWARDED", "CANCELLED"}
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "msclkid"}


def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_utc(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_fixtures(fixtures_dir=FIXTURES_DIR):
    return [load_json(path) for path in sorted(fixtures_dir.glob("*.json"))]


def opponent_name(fixture):
    home = fixture["homeTeam"]["name"]
    away = fixture["awayTeam"]["name"]
    return away if "Liverpool" in home else home


def task_from_fixture(task_type, fixture, rationale):
    return {
        "type": task_type,
        "fixture_id": fixture["id"],
        "matchweek": fixture.get("matchday"),
        "opponent": opponent_name(fixture),
        "kickoff": fixture["utcDate"],
        "rationale": rationale,
    }


def _latest_finished(fixtures, now):
    eligible = [
        fixture
        for fixture in fixtures
        if fixture.get("status") == "FINISHED" and parse_utc(fixture["utcDate"]) < now
    ]
    return max(eligible, key=lambda item: parse_utc(item["utcDate"]), default=None)


def _next_fixture(fixtures, now):
    eligible = [
        fixture
        for fixture in fixtures
        if fixture.get("status") not in TERMINAL_STATUSES
        and parse_utc(fixture["utcDate"]) > now
    ]
    return min(eligible, key=lambda item: parse_utc(item["utcDate"]), default=None)


def _post_match_due(fixture, now, next_fixture, research_dir):
    not_before = parse_utc(fixture["utcDate"]) + timedelta(hours=24)
    if now < not_before:
        return False
    if next_fixture and now >= parse_utc(next_fixture["utcDate"]):
        return False

    draft_path = research_dir / f"matchweek_{fixture.get('matchday', 0):02d}_{fixture['id']}.json"
    if not draft_path.exists():
        return True
    draft = load_json(draft_path)
    last_searched = draft.get("research_window", {}).get("last_searched_at")
    return last_searched is None or now >= parse_utc(last_searched) + timedelta(hours=20)


def plan_tasks(fixtures, now=None, research_dir=RESEARCH_DIR, force=False):
    now = now or datetime.now(timezone.utc)
    tasks = []
    next_fixture = _next_fixture(fixtures, now)
    latest_finished = _latest_finished(fixtures, now)

    if latest_finished and (
        force or _post_match_due(latest_finished, now, next_fixture, research_dir)
    ):
        post_match_rationale = (
            "A forced review run requested the latest finished match outside the normal due-window gate."
            if force
            else "The latest finished match is inside its review window and a research pass is due."
        )
        tasks.append(
            task_from_fixture(
                "post_match",
                latest_finished,
                post_match_rationale,
            )
        )

    if next_fixture:
        hours_until = (parse_utc(next_fixture["utcDate"]) - now).total_seconds() / 3600
        if force or 48 <= hours_until <= 72:
            pre_match_rationale = (
                f"A forced review run requested the next fixture with {hours_until:.1f} hours until kickoff, "
                "outside the normal timing gate."
                if force and not 48 <= hours_until <= 72
                else "The next Liverpool fixture is inside the 48-to-72-hour Game Plan window."
            )
            tasks.append(
                task_from_fixture(
                    "pre_match",
                    next_fixture,
                    pre_match_rationale,
                )
            )
    return tasks


def build_context(tasks):
    fixture_ids = {task["fixture_id"] for task in tasks}
    fixtures = {
        fixture["id"]: fixture
        for fixture in load_fixtures()
        if fixture["id"] in fixture_ids
    }
    drafts = []
    for path in sorted(RESEARCH_DIR.glob("*.json")):
        draft = load_json(path)
        if draft.get("match_id") in fixture_ids:
            drafts.append(draft)
    return {
        "tasks": tasks,
        "fixtures": fixtures,
        "current_lineup_projection": load_json(PROJECTION_PATH),
        "manager_prior": load_json(PRIOR_PATH),
        "squad": load_json(SQUAD_PATH),
        "player_profiles": [
            load_json(path) for path in sorted(PLAYER_PROFILES_DIR.glob("*.json"))
        ],
        "existing_research_drafts": drafts,
    }


def api_payload(tasks, model):
    schema = load_json(PACKET_SCHEMA_PATH)
    schema.pop("$schema", None)
    return {
        "model": model,
        "store": False,
        "instructions": PROMPT_PATH.read_text(encoding="utf-8"),
        "input": json.dumps(build_context(tasks), ensure_ascii=False),
        "tools": [{"type": "web_search"}],
        "tool_choice": "auto",
        "include": ["web_search_call.action.sources"],
        "max_tool_calls": 12,
        "max_output_tokens": 12000,
        "reasoning": {"effort": "medium"},
        "text": {
            "format": {
                "type": "json_schema",
                "name": "liverpool_research_packet",
                "strict": True,
                "schema": schema,
            }
        },
    }


def call_responses_api(payload, api_key, timeout=180):
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"OpenAI Responses API returned HTTP {error.code}: {detail}") from error


def extract_output_text(response):
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content["text"]
    raise RuntimeError("OpenAI response did not contain output_text")


def extract_web_source_urls(response):
    urls = set()
    for item in response.get("output", []):
        if item.get("type") != "web_search_call":
            continue
        for source in item.get("action", {}).get("sources", []):
            if source.get("url"):
                urls.add(source["url"])
    return urls


def canonical_source_url(url):
    """Return a conservative comparison key for a web provenance URL.

    Fragments never reach an HTTP server. Default ports, a final slash, and
    recognized marketing parameters likewise do not identify different source
    evidence. Everything else, including scheme, host, path, and non-tracking
    query parameters, remains significant.
    """
    try:
        parsed = urllib.parse.urlsplit(url.strip())
        port = parsed.port
    except (AttributeError, TypeError, ValueError):
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None
    if parsed.username or parsed.password:
        return None

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query_pairs = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ]
    query = urllib.parse.urlencode(query_pairs, doseq=True)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def reconcile_source_urls(packet, allowed_source_urls):
    """Replace harmless URL variants with one exact API-recorded URL.

    A normalized value is accepted only when it maps to exactly one provenance
    URL. Ambiguous or unrelated values remain untouched and are subsequently
    removed by the fail-closed evidence guard.
    """
    canonical_allowed = {}
    for url in allowed_source_urls:
        key = canonical_source_url(url)
        if key is not None:
            canonical_allowed.setdefault(key, set()).add(url)

    result = {"exact": 0, "reconciled": [], "unmatched": []}
    for source in packet.get("sources", []):
        proposed = source.get("url")
        if proposed in allowed_source_urls:
            result["exact"] += 1
            continue
        candidates = canonical_allowed.get(canonical_source_url(proposed), set())
        if len(candidates) == 1:
            recorded = next(iter(candidates))
            source["url"] = recorded
            result["reconciled"].append(
                {"source_id": source.get("id"), "proposed_url": proposed, "recorded_url": recorded}
            )
        else:
            result["unmatched"].append(
                {
                    "source_id": source.get("id"),
                    "proposed_url": proposed,
                    "candidate_count": len(candidates),
                }
            )
    return result


def discard_ungrounded_evidence(packet, allowed_source_urls):
    """Remove sources absent from the API's web-search provenance record.

    Model output is untrusted even when it conforms to the JSON schema. A bad
    source must not invalidate grounded evidence from the same run, but every
    dependent claim or recommendation must be removed with it.
    """
    ungrounded_ids = {
        source["id"]
        for source in packet.get("sources", [])
        if source.get("url") not in allowed_source_urls
    }
    packet["sources"] = [
        source for source in packet["sources"] if source["id"] not in ungrounded_ids
    ]
    declared_ids = {source["id"] for source in packet["sources"]}
    removed = {"sources": len(ungrounded_ids)}
    for collection in ("claims", "recommendations"):
        before = len(packet[collection])
        packet[collection] = [
            item
            for item in packet[collection]
            if not (set(item["source_ids"]) - declared_ids)
        ]
        removed[collection] = before - len(packet[collection])

    if not any(removed.values()):
        return removed

    packet["uncertainties"].append(
        "The automated provenance guard discarded ungrounded or undeclared evidence: "
        f"{removed['sources']} ungrounded source(s), "
        f"{removed['claims']} dependent claim(s), and "
        f"{removed['recommendations']} dependent recommendation(s)."
    )
    return removed


def validate_packet(packet, tasks, allowed_source_urls=None):
    schema = load_json(PACKET_SCHEMA_PATH)
    errors = validate_schema(packet, schema)
    if errors:
        raise ValidationError("AI research packet failed schema validation:\n" + "\n".join(errors))

    expected = {(task["type"], task["fixture_id"]) for task in tasks}
    received = {(task["type"], task["fixture_id"]) for task in packet["tasks"]}
    if received != expected:
        raise ValidationError("AI packet tasks do not match the deterministic due-task plan")

    source_ids = [source["id"] for source in packet["sources"]]
    if len(source_ids) != len(set(source_ids)):
        raise ValidationError("AI packet contains duplicate source IDs")
    declared = set(source_ids)
    if allowed_source_urls is not None:
        ungrounded = {
            source["url"] for source in packet["sources"] if source["url"] not in allowed_source_urls
        }
        if ungrounded:
            raise ValidationError(
                "AI packet contains URLs absent from the web-search tool record: "
                f"{sorted(ungrounded)}"
            )
    task_fixture_ids = {task["fixture_id"] for task in packet["tasks"]}
    for item in [*packet["claims"], *packet["recommendations"]]:
        if item["fixture_id"] not in task_fixture_ids:
            raise ValidationError(
                f"AI packet item references fixture {item['fixture_id']} without a matching task"
            )
        if not item["source_ids"]:
            raise ValidationError("Every AI packet claim and recommendation must cite a source")
        if len(item["source_ids"]) != len(set(item["source_ids"])):
            raise ValidationError("AI packet items must not cite the same source more than once")
        unknown = set(item["source_ids"]) - declared
        if unknown:
            raise ValidationError(f"AI packet cites undeclared sources: {sorted(unknown)}")

    for task in packet["tasks"]:
        if task["type"] != "pre_match":
            continue
        fixture_id = task["fixture_id"]
        claim_categories = {
            item["category"] for item in packet["claims"] if item["fixture_id"] == fixture_id
        }
        recommendation_categories = {
            item["category"]
            for item in packet["recommendations"]
            if item["fixture_id"] == fixture_id
        }
        missing = []
        if "projected_lineup" not in claim_categories:
            missing.append("projected_lineup claim")
        if "prediction" not in recommendation_categories:
            missing.append("prediction recommendation")
        if "goalscorer_prediction" not in recommendation_categories:
            missing.append("goalscorer_prediction recommendation")
        if missing:
            raise ValidationError(
                f"Pre-match fixture {fixture_id} is incomplete; missing {', '.join(missing)}"
            )
    if not packet["human_review"]["required"]:
        raise ValidationError("AI research packets must require human review")


def write_failure_diagnostics(path, *, now, tasks, proposed_sources, allowed_urls, reconciliation, error):
    """Write credential-free provenance diagnostics for a failed review run."""
    diagnostics = {
        "diagnostic_version": 1,
        "generated_at": iso_utc(now),
        "tasks": tasks,
        "validation_error": str(error),
        "proposed_sources": proposed_sources,
        "web_search_provenance_urls": sorted(allowed_urls),
        "reconciliation": reconciliation,
    }
    path.write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_github_output(path, tasks):
    if not path:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"due={'true' if tasks else 'false'}\n")
        handle.write(f"task_count={len(tasks)}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="Print due tasks without calling an API")
    parser.add_argument("--force", action="store_true", help="Build tasks outside normal windows")
    parser.add_argument("--now", help="Override current UTC time for deterministic checks")
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    now = parse_utc(args.now) if args.now else datetime.now(timezone.utc)
    tasks = plan_tasks(load_fixtures(), now=now, force=args.force)
    write_github_output(args.github_output, tasks)
    if args.plan or not tasks:
        print(json.dumps({"due": bool(tasks), "tasks": tasks}, indent=2))
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required when research tasks are due")
    model = os.environ.get("OPENAI_RESEARCH_MODEL", "gpt-5.6-luna")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    response = call_responses_api(api_payload(tasks, model), api_key)
    packet = json.loads(extract_output_text(response))
    packet["generated_at"] = iso_utc(now)
    allowed_source_urls = extract_web_source_urls(response)
    proposed_sources = [
        {"id": source.get("id"), "url": source.get("url")}
        for source in packet.get("sources", [])
    ]
    reconciliation = reconcile_source_urls(packet, allowed_source_urls)
    if reconciliation["reconciled"]:
        print(
            "Reconciled harmless URL differences for "
            f"{len(reconciliation['reconciled'])} source(s) using API-recorded values"
        )
    removed = discard_ungrounded_evidence(packet, allowed_source_urls)
    if any(removed.values()):
        print(
            "Discarded ungrounded or undeclared AI evidence before validation: "
            f"{removed['sources']} source(s), {removed['claims']} claim(s), "
            f"{removed['recommendations']} recommendation(s)"
        )
    try:
        validate_packet(packet, tasks, allowed_source_urls=allowed_source_urls)
    except ValidationError as error:
        diagnostic_path = args.output_dir / f"research_diagnostics_{stamp}.json"
        write_failure_diagnostics(
            diagnostic_path,
            now=now,
            tasks=tasks,
            proposed_sources=proposed_sources,
            allowed_urls=allowed_source_urls,
            reconciliation=reconciliation,
            error=error,
        )
        print(f"Wrote failed-run diagnostics: {diagnostic_path}")
        raise

    path = args.output_dir / f"research_packet_{stamp}.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate_file(path, PACKET_SCHEMA_PATH)
    print(f"Wrote review-only research packet: {path}")


if __name__ == "__main__":
    main()
