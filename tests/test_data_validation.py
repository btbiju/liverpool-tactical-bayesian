import tempfile
import unittest
from pathlib import Path

from pipeline.build_posteriors import build_snapshots, check_snapshots, write_snapshots
from pipeline.validate_data import REPO_ROOT, validate_all, validate_file, validate_schema


class SchemaValidatorTests(unittest.TestCase):
    def test_rejects_missing_required_property(self):
        errors = validate_schema({}, {"type": "object", "required": ["name"]})
        self.assertTrue(errors)

    def test_rejects_invalid_nested_type(self):
        schema = {
            "type": "object",
            "properties": {"confidence": {"type": "number", "minimum": 0, "maximum": 1}},
        }
        self.assertTrue(validate_schema({"confidence": "high"}, schema))
        self.assertTrue(validate_schema({"confidence": 2}, schema))

    def test_committed_project_data_and_identifiers_validate(self):
        counts = validate_all()
        self.assertEqual(counts["manager_priors"], 1)
        self.assertEqual(counts["player_profiles"], 30)
        self.assertEqual(counts["squad_players"], 30)

    def test_controlled_observation_builds_a_valid_posterior_end_to_end(self):
        fixture = REPO_ROOT / "tests" / "fixtures" / "sample_match_observation.json"
        observation_schema = REPO_ROOT / "schema" / "match_observation.schema.json"
        posterior_schema = REPO_ROOT / "schema" / "posterior_state.schema.json"
        validate_file(fixture, observation_schema)

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            observations = temporary / "observations"
            output = temporary / "posteriors"
            observations.mkdir()
            (observations / "matchweek_01_999001.json").write_text(
                fixture.read_text(encoding="utf-8"), encoding="utf-8"
            )

            snapshots = build_snapshots(observations_dir=observations)
            self.assertEqual(list(snapshots), ["matchweek_01.json"])
            self.assertEqual(snapshots["matchweek_01.json"]["as_of_matchweek"], 1)
            self.assertEqual(len(snapshots["matchweek_01.json"]["update_log"]), 1)

            write_snapshots(snapshots, output)
            check_snapshots(snapshots, output)
            validate_file(output / "matchweek_01.json", posterior_schema)


if __name__ == "__main__":
    unittest.main()
