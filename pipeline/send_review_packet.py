"""Send a validated research packet to the private review console.

The packet is signed with HMAC-SHA256. This helper never reads repository data
other than the explicit packet path and does not print credentials.
"""

import argparse
import hashlib
import hmac
import json
import urllib.error
import urllib.request
from pathlib import Path


def canonical_envelope(packet, github_run_id=None):
    payload = {"packet": packet}
    if github_run_id:
        payload["github_run_id"] = str(github_run_id)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def signature(secret, body):
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def send_packet(packet_path, console_url, secret, github_run_id=None, timeout=30):
    with packet_path.open(encoding="utf-8") as handle:
        packet = json.load(handle)
    body = canonical_envelope(packet, github_run_id)
    request = urllib.request.Request(
        f"{console_url.rstrip('/')}/api/packets",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Review-Signature": signature(secret, body),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Review console returned HTTP {error.code}: {detail}"
        ) from error
    print(f"Queued review packet {result['id']} ({result['status']})")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--console-url", required=True)
    parser.add_argument("--secret", required=True)
    parser.add_argument("--github-run-id")
    args = parser.parse_args()
    send_packet(
        args.packet,
        args.console_url,
        args.secret,
        github_run_id=args.github_run_id,
    )


if __name__ == "__main__":
    main()
