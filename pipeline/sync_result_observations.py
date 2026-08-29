"""Create deterministic result-only observations from finished raw fixtures.

This automation intentionally uses only facts available in football-data.org:
the final score and the resulting goals-conceded value. Tactical fields remain
null until a compatible source is reviewed. Existing human-reviewed
observations are never overwritten.
"""

import argparse
import json
from pathlib import Path

try:
    from .validate_data import REPO_ROOT
except ImportError:  # Support direct execution.
    from validate_data import REPO_ROOT


DEFAULT_FIXTURES = REPO_ROOT / "data" / "fixtures"
DEFAULT_OBSERVATIONS = REPO_ROOT / "data" / "observations"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def result_details(match):
    home_name = match["homeTeam"]["name"]
    away_name = match["awayTeam"]["name"]
    is_home = "Liverpool" in home_name
    opponent = away_name if is_home else home_name
    score = match["score"]["fullTime"]
    home_goals = score["home"]
    away_goals = score["away"]
    if home_goals is None or away_goals is None:
        raise ValueError(f"finished match {match['id']} has no full-time score")
    goals_for = home_goals if is_home else away_goals
    goals_against = away_goals if is_home else home_goals
    outcome = "W" if goals_for > goals_against else "D" if goals_for == goals_against else "L"
    return {
        "opponent": f"{opponent.removesuffix(' FC')} ({'H' if is_home else 'A'})",
        "result": f"{outcome} {goals_for}-{goals_against}",
        "goals_against": goals_against,
    }


def automated_observation(match):
    if match.get("status") != "FINISHED":
        raise ValueError(f"match {match.get('id')} is not FINISHED")
    details = result_details(match)
    match_id = match["id"]
    recorded_at = match.get("lastUpdated") or match["utcDate"]
    accessed_at = recorded_at[:10]
    return {
        "observation_kind": "automated_result_only",
        "match_id": match_id,
        "matchweek": match["matchday"],
        "date": match["utcDate"][:10],
        "opponent": details["opponent"],
        "result": details["result"],
        "metrics": {
            "possession_pct": None,
            "ppda": None,
            "shots_on_target_per_match": None,
            "goals_conceded_per_match": details["goals_against"],
            "accurate_passes_per_match": None,
            "accurate_crosses_per_match": None,
        },
        "formation": None,
        "sources": [
            {
                "id": "football-data-result",
                "name": "football-data.org — automated final result record",
                "url": f"https://api.football-data.org/v4/matches/{match_id}",
                "accessed_at": accessed_at,
                "notes": "Authenticated API record committed verbatim in data/fixtures; used only for score-derived facts.",
            }
        ],
        "metric_sources": {
            "goals_conceded_per_match": ["football-data-result"],
        },
        "reviewed_at": recorded_at,
        "notes": [
            "Created automatically after the raw fixture reached FINISHED status.",
            "Only goals conceded is updated because it follows exactly from the verified final score.",
            "Possession, PPDA, shots on target, accurate passes, accurate crosses, and formation remain null; none are inferred from the result.",
            "A later human tactical review may enrich this same observation without double-counting the matchweek.",
        ],
    }


def existing_by_match_id(observations_dir):
    existing = {}
    if not observations_dir.exists():
        return existing
    for path in observations_dir.glob("*.json"):
        if path.name.endswith(".template.json"):
            continue
        observation = load_json(path)
        existing[observation["match_id"]] = (path, observation)
    return existing


def sync_result_observations(fixtures_dir=DEFAULT_FIXTURES, observations_dir=DEFAULT_OBSERVATIONS):
    observations_dir.mkdir(parents=True, exist_ok=True)
    existing = existing_by_match_id(observations_dir)
    written = []
    skipped_human = []
    fixtures = sorted(
        (load_json(path) for path in fixtures_dir.glob("*.json")),
        key=lambda match: (match.get("matchday") or 999, match["id"]),
    )
    for match in fixtures:
        if match.get("status") != "FINISHED":
            continue
        current = existing.get(match["id"])
        if current and current[1].get("observation_kind", "human_reviewed") == "human_reviewed":
            skipped_human.append(match["id"])
            continue
        expected = automated_observation(match)
        path = current[0] if current else observations_dir / (
            f"matchweek_{match['matchday']:02d}_{match['id']}.json"
        )
        content = json.dumps(expected, indent=2, ensure_ascii=False) + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            written.append(path.name)
    return {"written": written, "skipped_human": skipped_human}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--observations-dir", type=Path, default=DEFAULT_OBSERVATIONS)
    args = parser.parse_args()
    result = sync_result_observations(args.fixtures_dir, args.observations_dir)
    print(
        f"Result observation sync complete: {len(result['written'])} written; "
        f"{len(result['skipped_human'])} human-reviewed observation(s) preserved."
    )


if __name__ == "__main__":
    main()
