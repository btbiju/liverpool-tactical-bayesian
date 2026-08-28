import unittest

from pipeline.bayesian_update import (
    apply_matchweek,
    formation_probabilities,
    update_dirichlet,
    update_normal_normal,
)


class NormalNormalUpdateTests(unittest.TestCase):
    def test_default_update_respects_virtual_match_weight(self):
        mean, variance, effective_n = update_normal_normal(10, 4, 10, 14)

        self.assertAlmostEqual(mean, (10 * 10 + 14) / 11)
        self.assertAlmostEqual(variance, 40 / 11)
        self.assertEqual(effective_n, 11)

    def test_sequential_default_updates_equal_a_rolling_mean(self):
        mean, variance, effective_n = update_normal_normal(10, 4, 10, 14)
        mean, variance, effective_n = update_normal_normal(
            mean, variance, effective_n, 14, observation_variance=40
        )

        self.assertAlmostEqual(mean, (10 * 10 + 14 + 14) / 12)
        self.assertAlmostEqual(variance, 40 / 12)
        self.assertEqual(effective_n, 12)

    def test_explicit_lower_observation_variance_has_more_influence(self):
        default_mean, _, _ = update_normal_normal(10, 4, 10, 14)
        precise_mean, _, _ = update_normal_normal(10, 4, 10, 14, observation_variance=4)

        self.assertGreater(precise_mean, default_mean)
        self.assertAlmostEqual(precise_mean, 12)

    def test_invalid_uncertainty_inputs_are_rejected(self):
        for variance, effective_n in [(0, 10), (-1, 10), (4, 0), (4, -1)]:
            with self.subTest(variance=variance, effective_n=effective_n):
                with self.assertRaises(ValueError):
                    update_normal_normal(10, variance, effective_n, 14)


class FormationUpdateTests(unittest.TestCase):
    def test_known_formation_increments_its_bucket(self):
        result = update_dirichlet({"4-2-3-1": 3, "other": 1}, "4-2-3-1")
        self.assertEqual(result, {"4-2-3-1": 4, "other": 1})

    def test_unknown_formation_increments_other(self):
        result = update_dirichlet({"4-2-3-1": 3, "other": 1}, "3-4-3")
        self.assertEqual(result, {"4-2-3-1": 3, "other": 2})

    def test_missing_formation_does_not_change_counts(self):
        original = {"4-2-3-1": 3, "other": 1}
        self.assertEqual(update_dirichlet(original, None), original)
        self.assertEqual(update_dirichlet(original, ""), original)

    def test_probabilities_are_normalized(self):
        probabilities = formation_probabilities({"4-2-3-1": 3, "other": 1})
        self.assertEqual(probabilities, {"4-2-3-1": 0.75, "other": 0.25})


class ApplyMatchweekTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "as_of_matchweek": 0,
            "continuous_metrics": {
                "ppda": {"mean": 10, "variance": 4, "effective_n": 10},
                "possession_pct": {"mean": 50, "variance": 4, "effective_n": 10},
            },
            "formation_prior": {
                "alpha": {"4-2-3-1": 3, "other": 1},
                "notes": "preserve this metadata",
            },
            "update_log": [],
        }

    def observation(self, **overrides):
        observation = {
            "matchweek": 1,
            "date": "2026-08-23",
            "opponent": "Example FC (H)",
            "result": "W 1-0",
            "metrics": {"ppda": 8},
            "formation": "4-2-3-1",
        }
        observation.update(overrides)
        return observation

    def test_update_persists_match_noise_for_sequential_updates(self):
        result = apply_matchweek(self.state, self.observation())
        metric = result["continuous_metrics"]["ppda"]

        self.assertAlmostEqual(metric["mean"], 9.818, places=3)
        self.assertAlmostEqual(metric["variance"], 3.6364, places=4)
        self.assertEqual(metric["effective_n"], 11)
        self.assertEqual(metric["observation_variance"], 40)
        self.assertEqual(result["formation_prior"]["notes"], "preserve this metadata")

    def test_explicit_observation_variance_is_used_and_persisted(self):
        observation = self.observation(observation_variances={"ppda": 4})
        result = apply_matchweek(self.state, observation)

        self.assertEqual(result["continuous_metrics"]["ppda"]["mean"], 9)
        self.assertEqual(result["continuous_metrics"]["ppda"]["observation_variance"], 4)

    def test_null_metrics_and_formation_are_ignored(self):
        observation = self.observation(
            metrics={"ppda": None},
            formation=None,
        )
        result = apply_matchweek(self.state, observation)

        self.assertEqual(result["continuous_metrics"]["ppda"], self.state["continuous_metrics"]["ppda"])
        self.assertEqual(result["formation_prior"], self.state["formation_prior"])
        self.assertEqual(result["update_log"][0]["metrics_observed"], {})


if __name__ == "__main__":
    unittest.main()
