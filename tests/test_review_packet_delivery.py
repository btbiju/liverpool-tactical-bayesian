import hashlib
import hmac
import json
import unittest

from pipeline.send_review_packet import (
    REVIEW_CONSOLE_USER_AGENT,
    build_request,
    canonical_envelope,
    signature,
)


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

    def test_request_identifies_the_repository_client_without_exposing_secret(self):
        body = b'{"packet":{"packet_version":1}}'
        request = build_request("https://review.example/", "test-secret", body)

        self.assertEqual(request.full_url, "https://review.example/api/packets")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.data, body)
        self.assertEqual(request.get_header("User-agent"), REVIEW_CONSOLE_USER_AGENT)
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(
            request.get_header("X-review-signature"),
            signature("test-secret", body),
        )
        self.assertNotIn("test-secret", repr(request.header_items()))


if __name__ == "__main__":
    unittest.main()
