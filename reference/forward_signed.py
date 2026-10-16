"""Signed multi-hop receiver/relay logic for Pharo-Lapse v3."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from envelope_v3 import deliver_once, forward_signed, verify_envelope


@dataclass
class SignedNode:
    """A small durable-policy boundary for tests and adapters.

    The caller owns durable storage. ``inbox`` and ``transit`` are explicit
    sets so a production adapter can replace them with SQLite transactions.
    """

    peer_id: str
    signing_key: Ed25519PrivateKey
    trusted_keys: Mapping[str, Ed25519PublicKey]
    inbox: set[str] = field(default_factory=set)
    transit: set[tuple[str, str]] = field(default_factory=set)

    def receive(self, envelope: dict, next_peer_id: Optional[str] = None) -> tuple[str, Optional[dict]]:
        verify_envelope(envelope, self.trusted_keys)
        if envelope["recipient_peer_id"] == self.peer_id:
            result = deliver_once(envelope, self.peer_id, self.trusted_keys, self.inbox)
            return result, None
        if next_peer_id is None:
            raise ValueError("NO_NEXT_HOP")
        key = (str(envelope["msg_id"]), str(envelope["origin_cid"]))
        if key in self.transit:
            return "DUPLICATE_TRANSIT", None
        forwarded = forward_signed(envelope, self.peer_id, self.signing_key, next_peer_id, self.trusted_keys)
        self.transit.add(key)
        return "FORWARDED", forwarded
