#!/usr/bin/env python3
"""Project Reclaim -> Pharo-Lapse adapter boundary.

This intentionally refuses to fabricate a production event. Project Reclaim's
operator must provide the authoritative event schema and an approved event
serializer before this adapter can emit a signed Pharo-Lapse payload.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REQUIRED_ENV = (
    "PROJECT_RECLAIM_EVENT_FILE",
    "PROJECT_RECLAIM_EVENT_SCHEMA",
    "PROJECT_RECLAIM_OPERATOR_APPROVAL",
)


def blocked(reason: str) -> int:
    print("PROJECT_RECLAIM_ADAPTER=BLOCKED")
    print(f"DEPENDENCY={reason}")
    return 4


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[:2] != ["pharo-lapse-outbox", "--output"]:
        return blocked("usage: adapter-template.py pharo-lapse-outbox --output OUTPUT_JSON")
    output = Path(argv[-1])
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        return blocked("operator must supply: " + ", ".join(missing))
    event_file = Path(os.environ["PROJECT_RECLAIM_EVENT_FILE"])
    if not event_file.is_file():
        return blocked("PROJECT_RECLAIM_EVENT_FILE does not exist")
    try:
        event = json.loads(event_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return blocked(f"event file is not valid UTF-8 JSON: {exc}")
    if not isinstance(event, dict):
        return blocked("Project Reclaim event must be a JSON object")
    return blocked(
        "authoritative Project Reclaim event schema and deterministic payload serializer "
        "are not defined; no payload was emitted"
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
