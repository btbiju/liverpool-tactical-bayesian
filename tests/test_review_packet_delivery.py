import hashlib
import hmac
import json
import unittest

from pipeline.send_review_packet import canonical_envelope, signature


class ReviewPacketDeliveryTests(unittest.TestCase):
    def test_envelope_is_compact_and_deterministic(self):
        packet = {"packet_version": 1, "uncertainties": []}
        body = canonical_envelope(packet, github_run_id=12345)
        self.assertEqual(
            body,
            b'{"packet":{"packet_version":1,"uncertainties":[]},"github_run_id":"12345"}',
        )

    def test_signature_is_hmac_sha256(self):
        body = json.dumps({"packet": {"packet_version": 1}}).encode()
        expected = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        self.assertEqual(signature("secret", body), expected)


if __name__ == "__main__":
    unittest.main()
