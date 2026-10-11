#!/usr/bin/env python3
"""Recovery -> Pharo-Lapse adapter template.

Replace load_authorized_payload() with the operator-approved Recovery
integration. No recovery event or message content is synthesized here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

PRODUCT_ID = "recovery"


def load_authorized_payload() -> str:
    source = os.environ.get("RECOVERY_PAYLOAD_FILE") or os.environ.get("PHARO_PRODUCT_PAYLOAD_FILE")
    if not source:
        raise RuntimeError("BLOCKED: set RECOVERY_PAYLOAD_FILE to an authorized payload file")
    path = Path(source)
    if not path.is_file():
        raise RuntimeError(f"BLOCKED: payload file does not exist: {path}")
    body = path.read_text(encoding="utf-8")
    if not body or len(body) > 4096:
        raise RuntimeError("BLOCKED: payload must be 1–4096 characters")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command != "pharo-lapse-outbox" or args.mode != "offline-reference-demo":
        raise SystemExit("BLOCKED: unsupported adapter invocation")
    if args.product_id != PRODUCT_ID:
        raise SystemExit(f"BLOCKED: expected --product-id {PRODUCT_ID}")
    result = {"product_id": PRODUCT_ID, "body": load_authorized_payload()}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
