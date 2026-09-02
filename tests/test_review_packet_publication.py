import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from pipeline.publish_reviewed_packet import canonical_packet, publish_export
from pipeline.validate_data import ValidationError


def sample_packet():
    return {
        "packet_version": 1,
        "generated_at": "2026-09-01T12:00:00Z",
        "tasks": [],
        "sources": [],
        "claims": [],
        "recommendations": [],
        "uncertainties": ["No explicit evidence was available."],
        "human_review": {
            "required": True,
            "prohibited_direct_writes": ["observations", "posteriors"],
            "review_notes": "Reviewed before publication.",
        },
    }


class ReviewPacketPublicationTests(unittest.TestCase):
    def test_verified_packet_is_written_without_mutation(self):
        packet = sample_packet()
        digest = hashlib.sha256(canonical_packet(packet)).hexdigest()
        packet_id = f"packet_{digest[:16]}"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_path = root / "export.json"
            export_path.write_text(
                json.dumps({"id": packet_id, "digest": digest, "packet": packet}),
                encoding="utf-8",
            )
            output = publish_export(export_path, packet_id, digest, output_dir=root / "out")
            self.assertEqual(json.loads(output.read_text()), packet)

    def test_digest_mismatch_is_rejected(self):
        packet = sample_packet()
        with tempfile.TemporaryDirectory() as directory:
            export_path = Path(directory) / "export.json"
            export_path.write_text(
                json.dumps({"id": "packet_0000000000000000", "digest": "bad", "packet": packet}),
                encoding="utf-8",
            )
            with self.assertRaises(ValidationError):
                publish_export(
                    export_path,
                    "packet_0000000000000000",
                    "bad",
                    output_dir=Path(directory) / "out",
                )


if __name__ == "__main__":
    unittest.main()
