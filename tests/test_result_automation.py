import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pipeline.fixture_refresh_due import refresh_due
from pipeline.sync_result_observations import automated_observation, sync_result_observations
from pipeline.validate_data import REPO_ROOT, validate_file


def sample_fixture(status="FINISHED"):
    return {
        "id": 700001,
        "utcDate": "2026-08-29T11:30:00Z",
        "status": status,
        "matchday": 2,
        "lastUpdated": "2026-08-29T13:28:00Z",
        "homeTeam": {"name": "Liverpool FC"},
        "awayTeam": {"name": "Nottingham Forest FC"},
        "score": {"fullTime": {"home": 3, "away": 1}},
    }


class RefreshGateTests(unittest.TestCase):
    def test_refresh_is_due_around_expected_full_time(self):
        fixture = sample_fixture(status="TIMED")
        now = datetime(2026, 8, 29, 13, 20, tzinfo=timezone.utc)
        self.assertTrue(refresh_due([fixture], now=now))

    def test_refresh_is_not_due_before_or_after_window(self):
        fixture = sample_fixture(status="TIMED")
        before = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)
        after = datetime(2026, 8, 30, 0, 0, tzinfo=timezone.utc)
        self.assertFalse(refresh_due([fixture], now=before))
        self.assertFalse(refresh_due([fixture], now=after))

    def test_finished_fixture_does_not_trigger_another_refresh(self):
        now = datetime(2026, 8, 29, 13, 30, tzinfo=timezone.utc)
        self.assertFalse(refresh_due([sample_fixture()], now=now))


class ResultObservationTests(unittest.TestCase):
    def test_automated_observation_updates_only_goals_conceded(self):
        observation = automated_observation(sample_fixture())
        self.assertEqual(observation["observation_kind"], "automated_result_only")
        self.assertEqual(observation["result"], "W 3-1")
        self.assertEqual(observation["opponent"], "Nottingham Forest (H)")
        self.assertEqual(observation["metrics"]["goals_conceded_per_match"], 1)
        self.assertTrue(
            all(
                value is None
                for name, value in observation["metrics"].items()
                if name != "goals_conceded_per_match"
            )
        )
        self.assertEqual(
            observation["metric_sources"],
            {"goals_conceded_per_match": ["football-data-result"]},
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "observation.json"
            path.write_text(json.dumps(observation), encoding="utf-8")
            validate_file(path, REPO_ROOT / "schema" / "match_observation.schema.json")

    def test_sync_writes_a_new_result_only_observation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fixtures = root / "fixtures"
            observations = root / "observations"
            fixtures.mkdir()
            (fixtures / "700001.json").write_text(
                json.dumps(sample_fixture()), encoding="utf-8"
            )

            result = sync_result_observations(fixtures, observations)

            self.assertEqual(result["written"], ["matchweek_02_700001.json"])
            created = json.loads(
                (observations / "matchweek_02_700001.json").read_text(encoding="utf-8")
            )
            self.assertEqual(created["observation_kind"], "automated_result_only")

    def test_sync_never_overwrites_human_review(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fixtures = root / "fixtures"
            observations = root / "observations"
            fixtures.mkdir()
            observations.mkdir()
            fixture = sample_fixture()
            (fixtures / "700001.json").write_text(json.dumps(fixture), encoding="utf-8")
            human_path = observations / "matchweek_02_700001.json"
            human = {"match_id": 700001, "observation_kind": "human_reviewed"}
            human_path.write_text(json.dumps(human), encoding="utf-8")

            result = sync_result_observations(fixtures, observations)

            self.assertEqual(result["written"], [])
            self.assertEqual(result["skipped_human"], [700001])
            self.assertEqual(json.loads(human_path.read_text(encoding="utf-8")), human)


if __name__ == "__main__":
    unittest.main()
