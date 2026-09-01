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
PROMPT_PATH = REPO_ROOT / "prompts" / "research_agent.md"
PACKET_SCHEMA_PATH = REPO_ROOT / "schema" / "agent_research_packet.schema.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "research_agent"
TERMINAL_STATUSES = {"FINISHED", "AWARDED", "CANCELLED"}


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
        tasks.append(
            task_from_fixture(
                "post_match",
                latest_finished,
                "The latest finished match is inside its review window and a research pass is due.",
            )
        )

    if next_fixture:
        hours_until = (parse_utc(next_fixture["utcDate"]) - now).total_seconds() / 3600
        if force or 48 <= hours_until <= 72:
            tasks.append(
                task_from_fixture(
                    "pre_match",
                    next_fixture,
                    "The next Liverpool fixture is inside the 48-to-72-hour Game Plan window.",
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
    for item in [*packet["claims"], *packet["recommendations"]]:
        unknown = set(item["source_ids"]) - declared
        if unknown:
            raise ValidationError(f"AI packet cites undeclared sources: {sorted(unknown)}")
    if not packet["human_review"]["required"]:
        raise ValidationError("AI research packets must require human review")


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
    response = call_responses_api(api_payload(tasks, model), api_key)
    packet = json.loads(extract_output_text(response))
    packet["generated_at"] = iso_utc(now)
    validate_packet(packet, tasks, allowed_source_urls=extract_web_source_urls(response))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    path = args.output_dir / f"research_packet_{stamp}.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate_file(path, PACKET_SCHEMA_PATH)
    print(f"Wrote review-only research packet: {path}")


if __name__ == "__main__":
    main()
