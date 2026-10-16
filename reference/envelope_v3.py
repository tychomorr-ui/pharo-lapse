"""Signed Pharo-Lapse v3 envelope primitives.

The origin signature covers the immutable origin fields, including the origin
route history and hop budget. Relay signatures cover append-only forwarding
records; the mutable current route is therefore authenticated without asking a
relay to forge the origin signature.
"""
from __future__ import annotations

import base64
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Mapping, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

MAX_HOPS = 8


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def unb64(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def public_key_b64(key: Ed25519PublicKey) -> str:
    return b64(key.public_bytes_raw())


def _origin_view(envelope: Mapping[str, object]) -> dict:
    """The origin signing domain, with the immutable origin route restored."""
    fields = {
        "msg_id", "created_at", "sender_peer_id", "recipient_peer_id", "body",
        "type", "phase", "lapse", "max_hops", "signed_by",
    }
    view = {key: envelope[key] for key in fields}
    view["route_history"] = envelope["origin_route_history"]
    return view


def _current_view(envelope: Mapping[str, object]) -> dict:
    return {key: value for key, value in envelope.items() if key != "cid"}


def _prefix_cid(envelope: Mapping[str, object], forwarding_count: int) -> str:
    """Reconstruct the CID immediately before forwarding_count was appended."""
    view = dict(envelope)
    view["route_history"] = list(envelope["origin_route_history"])
    view["forwarding"] = list(envelope["forwarding"][:forwarding_count])
    if forwarding_count:
        view["route_history"] = list(envelope["origin_route_history"]) + [
            record["peer_id"] for record in envelope["forwarding"][:forwarding_count]
        ]
    view["cid"] = "__ignored__"
    return sha256(_current_view(view))


def _record_view(record: Mapping[str, object]) -> dict:
    return {key: value for key, value in record.items() if key != "sig"}


def build_envelope(sender_peer_id: str, recipient_peer_id: str, body: str,
                   signing_key: Ed25519PrivateKey, *, msg_id: Optional[str] = None,
                   created_at: Optional[str] = None, phase: str = "DAY", lapse: int = 0,
                   max_hops: int = MAX_HOPS) -> dict:
    if not isinstance(body, str) or not body or len(body.encode("utf-8")) > 4096:
        raise ValueError("body must be a non-empty UTF-8 string of at most 4096 bytes")
    if not 1 <= max_hops <= 64:
        raise ValueError("max_hops must be between 1 and 64")
    if phase not in {"DAY", "NIGHT", "TWILIGHT"}:
        raise ValueError("invalid phase")
    route = [sender_peer_id]
    envelope = {
        "msg_id": msg_id or str(uuid.uuid4()),
        "created_at": created_at or utc_now(),
        "sender_peer_id": sender_peer_id,
        "recipient_peer_id": recipient_peer_id,
        "body": body,
        "type": "message",
        "phase": phase,
        "lapse": lapse,
        "route_history": list(route),
        "origin_route_history": list(route),
        "max_hops": max_hops,
        "signed_by": sender_peer_id,
        "forwarding": [],
    }
    envelope["sig"] = b64(signing_key.sign(canonical(_origin_view(envelope))))
    envelope["origin_cid"] = sha256({**_origin_view(envelope), "sig": envelope["sig"]})
    envelope["cid"] = sha256(_current_view(envelope))
    return envelope


def _verify_signature(public_key: Ed25519PublicKey, payload: object, signature_b64: str, label: str) -> None:
    try:
        public_key.verify(unb64(signature_b64), canonical(payload))
    except Exception as exc:
        raise ValueError(f"{label} signature invalid") from exc


def verify_envelope(envelope: Mapping[str, object], trusted_keys: Mapping[str, Ed25519PublicKey],
                    *, expected_recipient: Optional[str] = None) -> None:
    required = {"msg_id", "created_at", "sender_peer_id", "recipient_peer_id", "body", "type",
                "phase", "lapse", "route_history", "origin_route_history", "max_hops",
                "signed_by", "sig", "origin_cid", "forwarding", "cid"}
    missing = required - set(envelope)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if envelope["signed_by"] != envelope["sender_peer_id"]:
        raise ValueError("signed_by must equal sender_peer_id for the origin envelope")
    if expected_recipient is not None and envelope["recipient_peer_id"] != expected_recipient:
        raise ValueError("recipient mismatch")
    route = envelope["route_history"]
    origin_route = envelope["origin_route_history"]
    if not isinstance(route, list) or not isinstance(origin_route, list) or not route:
        raise ValueError("invalid route history")
    if route[:len(origin_route)] != origin_route or len(set(route)) != len(route):
        raise ValueError("invalid or repeated route history")
    if route[0] != envelope["sender_peer_id"]:
        raise ValueError("route must begin with sender")
    if not isinstance(envelope["max_hops"], int) or not 1 <= envelope["max_hops"] <= 64:
        raise ValueError("invalid max_hops")
    if len(route) - 1 > envelope["max_hops"]:
        raise ValueError("max_hops exceeded")
    sender_key = trusted_keys.get(str(envelope["sender_peer_id"]))
    if sender_key is None:
        raise ValueError("sender key is not pinned")
    _verify_signature(sender_key, _origin_view(envelope), str(envelope["sig"]), "origin")
    expected_origin = sha256({**_origin_view(envelope), "sig": envelope["sig"]})
    if envelope["origin_cid"] != expected_origin:
        raise ValueError("origin CID mismatch")
    if envelope["cid"] != sha256(_current_view(envelope)):
        raise ValueError("current CID mismatch")

    for index, record in enumerate(envelope["forwarding"]):
        if not isinstance(record, dict):
            raise ValueError("invalid forwarding record")
        for key in ("peer_id", "accepted_at", "lapse", "previous_cid", "next_peer_id", "route_history", "sig"):
            if key not in record:
                raise ValueError(f"forwarding record missing {key}")
        if record["previous_cid"] != _prefix_cid(envelope, index):
            raise ValueError("forwarding chain mismatch")
        if record["route_history"] != route[:len(origin_route) + index + 1]:
            raise ValueError("forwarding route mismatch")
        if record["peer_id"] != record["route_history"][-1]:
            raise ValueError("forwarding peer is not route tail")
        relay_key = trusted_keys.get(str(record["peer_id"]))
        if relay_key is None:
            raise ValueError(f"relay key is not pinned: {record['peer_id']}")
        _verify_signature(relay_key, _record_view(record), str(record["sig"]), "relay")


def forward_signed(envelope: Mapping[str, object], local_peer_id: str,
                   relay_key: Ed25519PrivateKey, next_peer_id: str,
                   trusted_keys: Mapping[str, Ed25519PublicKey]) -> dict:
    verify_envelope(envelope, trusted_keys)
    if local_peer_id in envelope["route_history"]:
        raise ValueError("LOOP_DETECTED")
    if len(envelope["route_history"]) - 1 >= envelope["max_hops"]:
        raise ValueError("MAX_HOPS_EXCEEDED")
    if next_peer_id in envelope["route_history"]:
        raise ValueError("NEXT_HOP_LOOP")
    updated = json.loads(json.dumps(envelope))
    previous_cid = updated["cid"]
    updated["route_history"].append(local_peer_id)
    record = {
        "peer_id": local_peer_id,
        "accepted_at": utc_now(),
        "lapse": updated["lapse"],
        "previous_cid": previous_cid,
        "next_peer_id": next_peer_id,
        "route_history": list(updated["route_history"]),
    }
    record["sig"] = b64(relay_key.sign(canonical(_record_view(record))))
    updated["forwarding"].append(record)
    updated["cid"] = sha256(_current_view(updated))
    return updated


def deliver_once(envelope: Mapping[str, object], local_peer_id: str,
                 trusted_keys: Mapping[str, Ed25519PublicKey], inbox: set[str]) -> str:
    verify_envelope(envelope, trusted_keys, expected_recipient=local_peer_id)
    msg_id = str(envelope["msg_id"])
    if msg_id in inbox:
        return "DUPLICATE"
    inbox.add(msg_id)
    return "DELIVERED"
