"""Validate and stage an owner-approved research packet for publication."""

import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from .validate_data import REPO_ROOT, ValidationError, validate_schema
except ImportError:
    from validate_data import REPO_ROOT, ValidationError, validate_schema


PACKET_SCHEMA = REPO_ROOT / "schema" / "agent_research_packet.schema.json"
OUTPUT_DIR = REPO_ROOT / "data" / "reviewed_packets"
ID_PATTERN = re.compile(r"^packet_[0-9a-f]{16}$")


def canonical_packet(packet):
    return json.dumps(packet, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def publish_export(export_path, expected_id, expected_digest, output_dir=OUTPUT_DIR):
    with export_path.open(encoding="utf-8") as handle:
        export = json.load(handle)
    if not ID_PATTERN.fullmatch(expected_id):
        raise ValidationError("review packet ID has an invalid format")
    if export.get("id") != expected_id or export.get("digest") != expected_digest:
        raise ValidationError("review-console export does not match the approved packet")

    packet = export.get("packet")
    if not isinstance(packet, dict):
        raise ValidationError("review-console export does not contain a packet object")
    actual_digest = hashlib.sha256(canonical_packet(packet)).hexdigest()
    if actual_digest != expected_digest:
        raise ValidationError("review packet digest verification failed")

    schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    errors = validate_schema(packet, schema)
    if errors:
        raise ValidationError("review packet failed schema validation:\n" + "\n".join(errors))
    if not packet.get("human_review", {}).get("required"):
        raise ValidationError("review packet must retain its human-review requirement")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{expected_id}.json"
    formatted = json.dumps(packet, indent=2, ensure_ascii=False) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != formatted:
        raise ValidationError("an existing reviewed packet cannot be overwritten")
    destination.write_text(formatted, encoding="utf-8")
    try:
        display_path = destination.relative_to(REPO_ROOT)
    except ValueError:
        display_path = destination
    print(f"Staged reviewed packet: {display_path}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--expected-id", required=True)
    parser.add_argument("--expected-digest", required=True)
    args = parser.parse_args()
    publish_export(args.export, args.expected_id, args.expected_digest)


if __name__ == "__main__":
    main()
