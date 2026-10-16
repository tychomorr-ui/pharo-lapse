#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter-template.py")


def run(event, approval="approved"):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        event_file = root / "event.json"
        output = root / "output.json"
        event_file.write_text(json.dumps(event), encoding="utf-8")
        env = os.environ.copy()
        env.update({
            "PROJECT_RECLAIM_EVENT_FILE": str(event_file),
            "PROJECT_RECLAIM_OPERATOR_APPROVAL": approval,
        })
        result = subprocess.run(
            [sys.executable, str(ADAPTER), "pharo-lapse-outbox", "--output", str(output)],
            env=env, text=True, capture_output=True,
        )
        return result, (output.read_text(encoding="utf-8") if output.exists() else "")


def main() -> int:
    missing = os.environ.copy()
    missing["PROJECT_RECLAIM_EVENT_FILE"] = "/no/such/project-reclaim-event.json"
    missing["PROJECT_RECLAIM_OPERATOR_APPROVAL"] = "approved"
    blocked = subprocess.run(
        [sys.executable, str(ADAPTER), "pharo-lapse-outbox", "--output", "/tmp/project-reclaim-output.json"],
        env=missing, text=True, capture_output=True,
    )
    assert blocked.returncode == 4
    assert "PROJECT_RECLAIM_ADAPTER=BLOCKED" in blocked.stdout

    event = {
        "event_id": "PR-TEST-001",
        "event_type": "status",
        "created_at": "2026-10-16T16:00:00Z",
        "priority": "routine",
        "origin": "project-reclaim",
        "message": "Project Reclaim reference status test",
    }
    result, output_text = run(event)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROJECT_RECLAIM_ADAPTER=READY" in result.stdout
    data = json.loads(output_text)
    assert data["product_id"] == "project-reclaim"
    body = json.loads(data["body"])
    assert body["schema"] == "PROJECT-RECLAIM-EVENT/1"
    assert body["event_id"] == "PR-TEST-001"

    invalid = dict(event, priority="emergency")
    result, _ = run(invalid)
    assert result.returncode == 4
    assert "priority must be one of" in result.stdout

    print("Project Reclaim adapter: READY for sanitized v1 reference events")
    print("Project Reclaim invalid-event rejection: PASS")
    print("No network delivery was attempted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
