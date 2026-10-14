"""Envelope v2 with multi-hop fields."""
import json
import uuid
from datetime import datetime, timezone
import hashlib

MAX_HOPS = 8

def build_envelope(sender_peer_id, recipient_peer_id, body,
                   route_history=None, max_hops=MAX_HOPS):
    envelope = {
        "msg_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sender_peer_id": sender_peer_id,
        "recipient_peer_id": recipient_peer_id,
        "body": body,
        "type": "message",
        "route_history": route_history or [],
        "max_hops": max_hops,
        "phase": "DAY",
        "lapse": 0,
    }
    canonical = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
    envelope["cid"] = hashlib.sha256(canonical.encode()).hexdigest()
    return envelope

def forward_envelope(envelope, local_peer_id):
    """Called when a node receives an envelope not addressed to it."""
    if local_peer_id in envelope["route_history"]:
        return None  # loop detected
    if len(envelope["route_history"]) >= envelope["max_hops"]:
        return None  # TTL exceeded
    envelope["route_history"].append(local_peer_id)
    # Recompute CID after modifying route_history
    canonical = json.dumps(
        {k: v for k, v in envelope.items() if k != "cid"},
        sort_keys=True, separators=(",", ":")
    )
    envelope["cid"] = hashlib.sha256(canonical.encode()).hexdigest()
    return envelope
