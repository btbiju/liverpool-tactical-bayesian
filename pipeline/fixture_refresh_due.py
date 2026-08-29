"""Gate frequent fixture refreshes to a small window around each match."""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from .validate_data import REPO_ROOT
except ImportError:  # Support direct execution.
    from validate_data import REPO_ROOT


DEFAULT_FIXTURES = REPO_ROOT / "data" / "fixtures"
TERMINAL_STATUSES = {"FINISHED", "AWARDED", "CANCELLED"}


def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def refresh_due(fixtures, now=None):
    now = now or datetime.now(timezone.utc)
    for match in fixtures:
        if match.get("status") in TERMINAL_STATUSES:
            continue
        kickoff = parse_utc(match["utcDate"])
        expected_finish = kickoff + timedelta(hours=1, minutes=45)
        if expected_finish - timedelta(minutes=15) <= now <= kickoff + timedelta(hours=10):
            return True
    return False


def load_fixtures(fixtures_dir):
    fixtures = []
    for path in fixtures_dir.glob("*.json"):
        with path.open(encoding="utf-8") as handle:
            fixtures.append(json.load(handle))
    return fixtures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    due = args.force or refresh_due(load_fixtures(args.fixtures_dir))
    value = "true" if due else "false"
    print(f"Fixture refresh due: {value}")
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            handle.write(f"due={value}\n")


if __name__ == "__main__":
    main()
