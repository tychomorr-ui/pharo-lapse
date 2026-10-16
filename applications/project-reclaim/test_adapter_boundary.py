#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter-template.py")


def main() -> int:
    env = os.environ.copy()
    env.update({
        "PROJECT_RECLAIM_EVENT_FILE": str(Path(__file__).with_name("missing-event.json")),
        "PROJECT_RECLAIM_EVENT_SCHEMA": "operator-pending",
        "PROJECT_RECLAIM_OPERATOR_APPROVAL": "operator-pending",
    })
    result = subprocess.run(
        [sys.executable, str(ADAPTER), "pharo-lapse-outbox", "--output", "/tmp/project-reclaim-output.json"],
        env=env, text=True, capture_output=True,
    )
    assert result.returncode == 4, result.stdout + result.stderr
    assert "PROJECT_RECLAIM_ADAPTER=BLOCKED" in result.stdout
    assert "PROJECT_RECLAIM_EVENT_FILE does not exist" in result.stdout
    print("Project Reclaim adapter boundary: BLOCKED as designed")
    print("No event was fabricated or queued")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
