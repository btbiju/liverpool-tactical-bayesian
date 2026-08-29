import unittest

from pipeline.resolve_research_draft import resolve_metric


def candidate(value, provider, group="possession_pct_full_match", source_id=None):
    return {
        "value": value,
        "source_id": source_id or provider.lower().replace(" ", "-"),
        "measurement_provider": provider,
        "compatibility_group": group,
        "evidence_location": "test fixture",
        "eligible_for_consensus": True,
    }


class ResearchResolutionTests(unittest.TestCase):
    def test_unanimous_independent_providers(self):
        resolved = resolve_metric([candidate(7, "Provider A"), candidate(7, "Provider B")])
        self.assertEqual(resolved["method"], "unanimous")
        self.assertEqual(resolved["value"], 7)

    def test_strict_majority_wins(self):
        resolved = resolve_metric(
            [candidate(61, "A"), candidate(61, "B"), candidate(58, "C")]
        )
        self.assertEqual(resolved["method"], "majority")
        self.assertEqual(resolved["value"], 61)
        self.assertEqual(resolved["measurement_providers"], ["A", "B"])

    def test_numeric_disagreement_uses_labeled_mean(self):
        resolved = resolve_metric(
            [candidate(60.8, "A"), candidate(58, "B"), candidate(61, "C")]
        )
        self.assertEqual(resolved["method"], "mean_consensus")
        self.assertEqual(resolved["value"], 59.933)
        self.assertEqual(resolved["range"], {"minimum": 58, "maximum": 61})
        self.assertEqual(resolved["between_provider_variance"], 1.8756)

    def test_duplicate_pages_from_one_provider_count_once(self):
        resolved = resolve_metric(
            [
                candidate(61, "Opta", source_id="club-opta"),
                candidate(61, "Opta", source_id="opta-analyst"),
                candidate(58, "Other"),
            ]
        )
        self.assertEqual(resolved["method"], "mean_consensus")
        self.assertEqual(resolved["value"], 59.5)

    def test_incompatible_definitions_are_not_combined(self):
        resolved = resolve_metric(
            [
                candidate(61, "A", group="full_match"),
                candidate(58, "B", group="full_match"),
                candidate(55, "C", group="first_half"),
            ]
        )
        self.assertEqual(resolved["compatibility_group"], "full_match")
        self.assertEqual(resolved["value"], 59.5)

    def test_categorical_tie_remains_unresolved(self):
        resolved = resolve_metric(
            [candidate("4-2-3-1", "A", "starting_formation"), candidate("4-3-3", "B", "starting_formation")]
        )
        self.assertEqual(resolved["status"], "unresolved")
        self.assertIsNone(resolved["value"])


if __name__ == "__main__":
    unittest.main()
