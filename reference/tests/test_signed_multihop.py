import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from envelope_v3 import build_envelope, forward_signed, verify_envelope
from forward_signed import SignedNode


class SignedMultihopTests(unittest.TestCase):
    def setUp(self):
        self.keys = {peer: Ed25519PrivateKey.generate() for peer in ("node-a", "node-b", "node-c", "node-d")}
        self.public = {peer: key.public_key() for peer, key in self.keys.items()}
        self.origin = build_envelope("node-a", "node-c", "HELLO-FROM-A", self.keys["node-a"], msg_id="signed-0001")

    def hop(self, envelope, relay, next_peer):
        return forward_signed(envelope, relay, self.keys[relay], next_peer, self.public)

    def test_sign_forward_a_b_c_verify_at_c(self):
        b = self.hop(self.origin, "node-b", "node-c")
        c = self.hop(b, "node-c", "node-c-final")
        verify_envelope(c, self.public, expected_recipient="node-c")
        self.assertEqual(c["route_history"], ["node-a", "node-b", "node-c"])
        self.assertEqual(len(c["forwarding"]), 2)

    def test_tamper_body_at_b_rejected_at_c(self):
        b = self.hop(self.origin, "node-b", "node-c")
        b["body"] = "TAMPERED"
        with self.assertRaises(ValueError):
            verify_envelope(b, self.public)

    def test_tamper_route_history_at_b_rejected_at_c(self):
        b = self.hop(self.origin, "node-b", "node-c")
        b["route_history"][1] = "evil-relay"
        with self.assertRaises(ValueError):
            verify_envelope(b, self.public)

    def test_replay_at_b_is_deduplicated(self):
        b_node = SignedNode("node-b", self.keys["node-b"], self.public)
        first, forwarded = b_node.receive(self.origin, "node-c")
        second, again = b_node.receive(self.origin, "node-c")
        self.assertEqual(first, "FORWARDED")
        self.assertIsNotNone(forwarded)
        self.assertEqual(second, "DUPLICATE_TRANSIT")
        self.assertIsNone(again)

    def test_loop_a_b_c_b_dropped(self):
        b = self.hop(self.origin, "node-b", "node-c")
        c = self.hop(b, "node-c", "node-d")
        with self.assertRaisesRegex(ValueError, "LOOP_DETECTED"):
            self.hop(c, "node-b", "node-c")

    def test_ttl_exceeded(self):
        limited = build_envelope("node-a", "node-d", "TTL", self.keys["node-a"], msg_id="ttl-0001", max_hops=2)
        b = self.hop(limited, "node-b", "node-c")
        c = self.hop(b, "node-c", "node-d")
        with self.assertRaisesRegex(ValueError, "MAX_HOPS_EXCEEDED"):
            self.hop(c, "node-d", "node-d-final")

    def test_missing_relay_signature_rejected(self):
        b = self.hop(self.origin, "node-b", "node-c")
        del b["forwarding"][0]["sig"]
        with self.assertRaises(ValueError):
            verify_envelope(b, self.public)

    def test_invalid_relay_signature_rejected(self):
        b = self.hop(self.origin, "node-b", "node-c")
        b["forwarding"][0]["sig"] = b["forwarding"][0]["sig"][:-2] + "AA"
        with self.assertRaises(ValueError):
            verify_envelope(b, self.public)


if __name__ == "__main__":
    unittest.main(verbosity=2)
