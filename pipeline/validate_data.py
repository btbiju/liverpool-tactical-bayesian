"""Offline validation for committed project JSON and cross-file invariants.

The repository intentionally has no Python dependencies. This module validates
the JSON Schema features used by the local schemas (types, required fields,
properties, pattern properties, arrays, enums, numeric bounds, and ISO dates)
and then applies project-specific consistency checks.
"""

import argparse
import json
import re
import subprocess
from datetime import date, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class ValidationError(ValueError):
    """Raised when committed project data violates its schema or invariants."""


def _matches_type(value, expected):
    types = expected if isinstance(expected, list) else [expected]
    python_types = {
        "object": dict,
        "array": list,
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "null": type(None),
    }
    return any(
        isinstance(value, python_types[item])
        and not (item in {"number", "integer"} and isinstance(value, bool))
        for item in types
    )


def validate_schema(value, schema, location="$"):
    """Return errors for the JSON Schema subset used by this repository."""
    errors = []
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(value, expected_type):
        return [f"{location}: expected {expected_type}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value is outside the allowed enum")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{location}: value is below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{location}: value is above maximum {schema['maximum']}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        patterns = [
            (re.compile(pattern), subschema)
            for pattern, subschema in schema.get("patternProperties", {}).items()
        ]
        for key, item in value.items():
            if key in properties:
                errors.extend(validate_schema(item, properties[key], f"{location}.{key}"))
            else:
                for pattern, subschema in patterns:
                    if pattern.search(key):
                        errors.extend(validate_schema(item, subschema, f"{location}.{key}"))

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors.extend(validate_schema(item, schema["items"], f"{location}[{index}]"))

    if isinstance(value, str) and schema.get("format") == "date":
        try:
            date.fromisoformat(value)
        except ValueError:
            errors.append(f"{location}: invalid ISO date")
    if isinstance(value, str) and schema.get("format") == "date-time":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{location}: invalid ISO date-time")

    return errors


def _load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_file(path, schema_path):
    errors = validate_schema(_load_json(path), _load_json(schema_path))
    if errors:
        formatted = "\n".join(f"  - {error}" for error in errors)
        raise ValidationError(f"{path.relative_to(REPO_ROOT)} failed validation:\n{formatted}")


def validate_observations(files, require_fixture_match=False):
    schema_path = REPO_ROOT / "schema" / "match_observation.schema.json"
    seen_match_ids = set()
    seen_matchweeks = set()
    fixture_dir = REPO_ROOT / "data" / "fixtures"
    known_metrics = set(
        _load_json(REPO_ROOT / "data" / "manager_priors" / "iraola_2026.json")[
            "continuous_metrics"
        ]
    )
    for path in files:
        validate_file(path, schema_path)
        observation = _load_json(path)
        if observation["match_id"] in seen_match_ids:
            raise ValidationError(f"duplicate observation match ID: {observation['match_id']}")
        if observation["matchweek"] in seen_matchweeks:
            raise ValidationError(f"duplicate observation matchweek: {observation['matchweek']}")
        seen_match_ids.add(observation["match_id"])
        seen_matchweeks.add(observation["matchweek"])

        if require_fixture_match:
            fixture_path = fixture_dir / f"{observation['match_id']}.json"
            if not fixture_path.exists():
                raise ValidationError(f"{path.name}: no raw fixture for match ID")
            fixture = _load_json(fixture_path)
            if fixture.get("status") != "FINISHED":
                raise ValidationError(f"{path.name}: raw fixture is not FINISHED")
            if fixture.get("matchday") != observation["matchweek"]:
                raise ValidationError(f"{path.name}: matchweek disagrees with raw fixture")
            if fixture.get("utcDate", "")[:10] != observation["date"]:
                raise ValidationError(f"{path.name}: date disagrees with raw fixture")
            home = fixture["homeTeam"]["name"]
            away = fixture["awayTeam"]["name"]
            is_home = "Liverpool" in home
            score = fixture["score"]["fullTime"]
            goals_for = score["home"] if is_home else score["away"]
            goals_against = score["away"] if is_home else score["home"]
            outcome = "W" if goals_for > goals_against else "D" if goals_for == goals_against else "L"
            expected_result = f"{outcome} {goals_for}-{goals_against}"
            if observation["result"] != expected_result:
                raise ValidationError(f"{path.name}: result disagrees with raw fixture")
            observed_goals_against = observation["metrics"].get("goals_conceded_per_match")
            if observed_goals_against != goals_against:
                raise ValidationError(
                    f"{path.name}: goals_conceded_per_match must match the final score"
                )

        unknown_metrics = set(observation["metrics"]) - known_metrics
        unknown_variances = set(observation.get("observation_variances", {})) - known_metrics
        if unknown_metrics or unknown_variances:
            raise ValidationError(
                f"{path.name}: unknown metric keys {sorted(unknown_metrics | unknown_variances)}"
            )

        source_ids = [source["id"] for source in observation["sources"]]
        if len(source_ids) != len(set(source_ids)):
            raise ValidationError(f"{path.name}: duplicate source IDs")
        declared = set(source_ids)
        metric_sources = observation["metric_sources"]
        evidenced_fields = {
            name for name, value in observation["metrics"].items() if value is not None
        }
        if observation.get("formation"):
            evidenced_fields.add("formation")
        if observation["observation_kind"] == "automated_result_only":
            if evidenced_fields != {"goals_conceded_per_match"}:
                raise ValidationError(
                    f"{path.name}: automated result-only observations may update only "
                    "goals_conceded_per_match"
                )
            if observation.get("observation_variances"):
                raise ValidationError(
                    f"{path.name}: automated result-only observations cannot override variance"
                )
        if not evidenced_fields:
            raise ValidationError(f"{path.name}: observation contains no usable evidence")
        for field in evidenced_fields:
            cited = metric_sources.get(field, [])
            if not cited:
                raise ValidationError(f"{path.name}: {field} has no source mapping")
            unknown = set(cited) - declared
            if unknown:
                raise ValidationError(f"{path.name}: {field} cites unknown sources {sorted(unknown)}")
        unsupported = set(metric_sources) - evidenced_fields
        if unsupported:
            raise ValidationError(
                f"{path.name}: source mappings exist for null/absent fields {sorted(unsupported)}"
            )


def tracked_json_files():
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.json"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [REPO_ROOT / line for line in output.splitlines() if (REPO_ROOT / line).is_file()]


def validate_all():
    manager_schema = REPO_ROOT / "schema" / "manager_prior.schema.json"
    player_schema = REPO_ROOT / "schema" / "player_profile.schema.json"
    posterior_schema = REPO_ROOT / "schema" / "posterior_state.schema.json"
    lineup_schema = REPO_ROOT / "schema" / "lineup_projection.schema.json"

    manager_files = sorted((REPO_ROOT / "data" / "manager_priors").glob("*.json"))
    player_files = sorted((REPO_ROOT / "data" / "player_profiles").glob("*.json"))
    posterior_dir = REPO_ROOT / "data" / "posteriors"
    posterior_files = sorted(posterior_dir.glob("*.json")) if posterior_dir.exists() else []
    observation_dir = REPO_ROOT / "data" / "observations"
    observation_files = sorted(
        path
        for path in observation_dir.glob("*.json")
        if not path.name.endswith(".template.json")
    )
    lineup_dir = REPO_ROOT / "data" / "lineup_projection"
    lineup_files = sorted(lineup_dir.glob("*.json")) if lineup_dir.exists() else []

    for path in tracked_json_files():
        _load_json(path)
    for path in manager_files:
        validate_file(path, manager_schema)
    for path in player_files:
        validate_file(path, player_schema)
    for path in posterior_files:
        validate_file(path, posterior_schema)
    for path in lineup_files:
        validate_file(path, lineup_schema)
    validate_observations(observation_files, require_fixture_match=True)

    squad = _load_json(REPO_ROOT / "data" / "squad" / "liverpool_2026_27.json")["players"]
    profiles = [_load_json(path) for path in player_files]
    squad_by_id = {str(player["fotmob_id"]): player for player in squad}
    if len(squad_by_id) != len(squad):
        raise ValidationError("squad contains duplicate FotMob IDs")
    if len({profile["player_id"] for profile in profiles}) != len(profiles):
        raise ValidationError("player profiles contain duplicate player IDs")
    if len(squad) != len(profiles):
        raise ValidationError(
            f"squad/profile count differs: {len(squad)} squad, {len(profiles)} profiles"
        )

    for profile in profiles:
        squad_player = squad_by_id.get(str(profile["fotmob_id"]))
        if squad_player is None:
            raise ValidationError(f"{profile['name']} is absent from the squad")
        if squad_player["name"] != profile["name"]:
            raise ValidationError(f"name mismatch for FotMob ID {profile['fotmob_id']}")
        if squad_player.get("squad_number") != profile.get("current_squad_number"):
            raise ValidationError(f"squad-number mismatch for {profile['name']}")

    profile_ids = {profile["player_id"] for profile in profiles}
    expected_lineup_slots = {
        "GK", "LB", "CB1", "CB2", "RB", "DM1", "DM2", "LW", "AM", "RW", "ST"
    }
    for path in lineup_files:
        projection = _load_json(path)
        slots = projection["projected_slots"]
        if set(slots) != expected_lineup_slots:
            raise ValidationError(f"{path.name}: projected lineup slots are incomplete")
        player_ids = list(slots.values())
        if len(player_ids) != len(set(player_ids)):
            raise ValidationError(f"{path.name}: projected lineup repeats a player")
        unknown_players = set(player_ids) - profile_ids
        if unknown_players:
            raise ValidationError(
                f"{path.name}: projected lineup references unknown players {sorted(unknown_players)}"
            )
        source_ids = [source["id"] for source in projection["sources"]]
        if len(source_ids) != len(set(source_ids)):
            raise ValidationError(f"{path.name}: duplicate lineup source IDs")
        declared_sources = set(source_ids)
        for item in projection["evidence"]:
            unknown_sources = set(item["source_ids"]) - declared_sources
            if unknown_sources:
                raise ValidationError(
                    f"{path.name}: lineup evidence cites unknown sources {sorted(unknown_sources)}"
                )

    return {
        "json_files": len(tracked_json_files()),
        "manager_priors": len(manager_files),
        "player_profiles": len(player_files),
        "posteriors": len(posterior_files),
        "lineup_projections": len(lineup_files),
        "observations": len(observation_files),
        "squad_players": len(squad),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate project JSON without network access")
    parser.parse_args()
    counts = validate_all()
    print(
        "Validation passed: "
        f"{counts['json_files']} JSON files parsed; "
        f"{counts['manager_priors']} manager prior, "
        f"{counts['player_profiles']} player profiles, "
        f"{counts['observations']} observations, "
        f"{counts['posteriors']} posteriors schema-checked; "
        f"{counts['lineup_projections']} lineup projections schema-checked; "
        f"{counts['squad_players']} squad identities cross-checked."
    )


if __name__ == "__main__":
    main()
