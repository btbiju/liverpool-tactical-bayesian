import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pipeline.research_agent import (
    discard_ungrounded_evidence,
    plan_tasks,
    validate_packet,
)
from pipeline.validate_data import ValidationError


def fixture(fixture_id, kickoff, status, matchday, opponent="Opponent FC"):
    return {
        "id": fixture_id,
        "utcDate": kickoff,
        "status": status,
        "matchday": matchday,
        "homeTeam": {"name": "Liverpool FC"},
        "awayTeam": {"name": opponent},
    }


class ResearchAgentPlanningTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)

    def test_pre_match_task_is_due_inside_48_to_72_hours(self):
        fixtures = [fixture(2, "2026-09-03T20:00:00Z", "TIMED", 3)]
        tasks = plan_tasks(fixtures, now=self.now)
        self.assertEqual([(task["type"], task["fixture_id"]) for task in tasks], [("pre_match", 2)])

    def test_pre_match_task_is_not_due_outside_window(self):
        fixtures = [fixture(2, "2026-09-05T20:00:00Z", "TIMED", 3)]
        self.assertEqual(plan_tasks(fixtures, now=self.now), [])

    def test_only_latest_finished_match_gets_post_match_task(self):
        fixtures = [
            fixture(1, "2026-08-20T20:00:00Z", "FINISHED", 1, "Old FC"),
            fixture(2, "2026-08-30T10:00:00Z", "FINISHED", 2, "Latest FC"),
            fixture(3, "2026-09-05T20:00:00Z", "TIMED", 3, "Next FC"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            tasks = plan_tasks(fixtures, now=self.now, research_dir=Path(directory))
        self.assertEqual([(task["type"], task["fixture_id"]) for task in tasks], [("post_match", 2)])

    def test_recent_research_attempt_blocks_another_daily_pass(self):
        fixtures = [
            fixture(2, "2026-08-30T10:00:00Z", "FINISHED", 2),
            fixture(3, "2026-09-05T20:00:00Z", "TIMED", 3),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matchweek_02_2.json"
            path.write_text(
                json.dumps({"research_window": {"last_searched_at": "2026-08-31T20:00:00Z"}}),
                encoding="utf-8",
            )
            self.assertEqual(plan_tasks(fixtures, now=self.now, research_dir=Path(directory)), [])


class ResearchAgentPacketTests(unittest.TestCase):
    def packet(self):
        return {
            "packet_version": 1,
            "generated_at": "2026-09-01T12:00:00Z",
            "tasks": [
                {
                    "type": "pre_match",
                    "fixture_id": 2,
                    "matchweek": 3,
                    "opponent": "Opponent FC",
                    "kickoff": "2026-09-03T20:00:00Z",
                    "rationale": "Inside the pre-match window.",
                }
            ],
            "sources": [
                {
                    "id": "official_1",
                    "title": "Official preview",
                    "url": "https://example.com/preview",
                    "published_at": "2026-09-01",
                    "accessed_at": "2026-09-01",
                    "source_tier": 1,
                    "medium": "article",
                    "measurement_provider": None,
                    "evidence_location": "Team news section",
                }
            ],
            "claims": [],
            "recommendations": [
                {
                    "fixture_id": 2,
                    "category": "lineup",
                    "summary": "Low-confidence selection recommendation",
                    "reasoning": "Based on the official availability update.",
                    "source_ids": ["official_1"],
                    "confidence": "low",
                }
            ],
            "uncertainties": ["No confirmed lineup is available."],
            "human_review": {
                "required": True,
                "prohibited_direct_writes": ["observations", "posteriors", "lineup_projection"],
                "review_notes": "Review before promotion.",
            },
        }

    def test_valid_packet_matches_planned_task(self):
        packet = self.packet()
        validate_packet(packet, packet["tasks"])

    def test_unknown_source_reference_is_rejected(self):
        packet = self.packet()
        packet["recommendations"][0]["source_ids"] = ["missing"]
        with self.assertRaises(ValidationError):
            validate_packet(packet, packet["tasks"])

    def test_url_absent_from_web_search_record_is_rejected(self):
        packet = self.packet()
        with self.assertRaises(ValidationError):
            validate_packet(packet, packet["tasks"], allowed_source_urls=set())

    def test_ungrounded_sources_and_dependent_items_are_discarded(self):
        packet = self.packet()
        packet["sources"].append(
            {
                **packet["sources"][0],
                "id": "ungrounded_1",
                "url": "https://example.com/unverified",
            }
        )
        packet["claims"].append(
            {
                "fixture_id": 2,
                "category": "availability",
                "claim": "Unsupported availability claim",
                "value": True,
                "unit": None,
                "source_ids": ["ungrounded_1"],
                "compatibility_group": None,
                "confidence": "low",
                "consensus_eligible": False,
            }
        )
        packet["recommendations"].append(
            {
                "fixture_id": 2,
                "category": "score",
                "summary": "Unsupported score recommendation",
                "reasoning": "Depends on an ungrounded source.",
                "source_ids": ["official_1", "ungrounded_1"],
                "confidence": "low",
            }
        )

        removed = discard_ungrounded_evidence(
            packet, {"https://example.com/preview"}
        )

        self.assertEqual(
            removed, {"sources": 1, "claims": 1, "recommendations": 1}
        )
        self.assertEqual([source["id"] for source in packet["sources"]], ["official_1"])
        self.assertEqual(packet["claims"], [])
        self.assertEqual(len(packet["recommendations"]), 1)
        self.assertIn("discarded 1 ungrounded source", packet["uncertainties"][-1])
        validate_packet(
            packet,
            packet["tasks"],
            allowed_source_urls={"https://example.com/preview"},
        )


if __name__ == "__main__":
    unittest.main()
