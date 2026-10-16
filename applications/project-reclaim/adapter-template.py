#!/usr/bin/env python3
"""Project Reclaim event adapter for the Pharo-Lapse reference queue.

Schema v1 intentionally contains no location or sensitive fields. This adapter
emits a deterministic body, but the legacy reference queue remains unsigned;
that limitation is reported by the bridge rather than hidden.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_ID = "project-reclaim"
SCHEMA = "PROJECT-RECLAIM-EVENT/1"
EVENT_TYPES = {"status", "fire", "medical", "supply", "outage"}
PRIORITIES = {"routine", "urgent", "critical"}
EVENT_ID_RE = re.compile(r"^PR-[A-Z0-9][A-Z0-9._-]{2,63}$")
REQUIRED = {"event_id", "event_type", "created_at", "priority", "origin", "message"}


def blocked(reason: str) -> int:
    print("PROJECT_RECLAIM_ADAPTER=BLOCKED")
    print(f"DEPENDENCY={reason}")
    return 4


def validate_event(event: object) -> dict:
    if not isinstance(event, dict):
        raise ValueError("event must be a JSON object")
    if set(event) != REQUIRED:
        raise ValueError(f"event fields must be exactly {sorted(REQUIRED)}")
    if not isinstance(event["event_id"], str) or not EVENT_ID_RE.fullmatch(event["event_id"]):
        raise ValueError("event_id must match PR-[A-Z0-9][A-Z0-9._-]{2,63}")
    if event["event_type"] not in EVENT_TYPES:
        raise ValueError(f"event_type must be one of {sorted(EVENT_TYPES)}")
    if event["priority"] not in PRIORITIES:
        raise ValueError(f"priority must be one of {sorted(PRIORITIES)}")
    if event["origin"] != PRODUCT_ID:
        raise ValueError("origin must be project-reclaim")
    if not isinstance(event["message"], str) or not 1 <= len(event["message"]) <= 1024:
        raise ValueError("message must be 1-1024 characters")
    try:
        parsed = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError("created_at must be an ISO-8601 UTC timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("created_at must include UTC Z or +00:00")
    normalized = dict(event)
    normalized["created_at"] = parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return normalized


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[:2] != ["pharo-lapse-outbox", "--output"]:
        return blocked("usage: adapter-template.py pharo-lapse-outbox --output OUTPUT_JSON")
    if os.environ.get("PROJECT_RECLAIM_OPERATOR_APPROVAL") != "approved":
        return blocked("set PROJECT_RECLAIM_OPERATOR_APPROVAL=approved for an operator-approved event")
    event_file = Path(os.environ.get("PROJECT_RECLAIM_EVENT_FILE", ""))
    if not event_file.is_file():
        return blocked("PROJECT_RECLAIM_EVENT_FILE does not exist")
    try:
        event = validate_event(json.loads(event_file.read_text(encoding="utf-8")))
    except Exception as exc:
        return blocked(str(exc))
    body = json.dumps({"schema": SCHEMA, **event}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    output = Path(argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"product_id": PRODUCT_ID, "body": body}, sort_keys=True) + "\n", encoding="utf-8")
    print("PROJECT_RECLAIM_ADAPTER=READY")
    print(f"EVENT_ID={event['event_id']}")
    print(f"OUTPUT={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
