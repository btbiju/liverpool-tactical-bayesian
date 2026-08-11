"""
Pulls Liverpool's fixtures from football-data.org and writes each match as
its own JSON file in data/fixtures/, matching the raw match shape the
dashboard's Fixtures tab already normalizes (see dashboard/src/tabs/FixturesTab.jsx).

Usage:
    export FOOTBALL_DATA_API_KEY=your_key_here
    python3 pipeline/pull_fixtures.py
"""
import json
import os

from fixtures_client import get_liverpool_fixtures

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures")


def main():
    fixtures = get_liverpool_fixtures()
    os.makedirs(OUT_DIR, exist_ok=True)

    existing = {f for f in os.listdir(OUT_DIR) if f.endswith(".json")}
    written = set()

    for match in fixtures:
        filename = f"{match['id']}.json"
        with open(os.path.join(OUT_DIR, filename), "w") as f:
            json.dump(match, f, indent=2)
        written.add(filename)

    stale = existing - written
    for filename in stale:
        os.remove(os.path.join(OUT_DIR, filename))

    print(f"Wrote {len(written)} fixtures to {OUT_DIR}")
    if stale:
        print(f"Removed {len(stale)} stale fixture file(s) no longer returned by the API: {sorted(stale)}")


if __name__ == "__main__":
    main()
