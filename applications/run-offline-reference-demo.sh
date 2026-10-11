#!/usr/bin/env bash
# Dimension 5 offline reference demonstration runner.
#
# This script intentionally does not synthesize an application payload, peer ID,
# public key, message ID, receipt, or live result. It needs an operator-supplied
# real product adapter before it can run. The local listener used after the
# stopped-listener step is reference/phone_inbox_dedup.py, not a product runtime.
set -Eeuo pipefail

PRODUCT_ID="${1:-}"
case "$PRODUCT_ID" in
  pd-pro|task-force-pro|recovery|iwa-sage) ;;
  *)
    printf 'DEMO_EXECUTION=BLOCKED\nDEPENDENCY=first argument must be one of pd-pro, task-force-pro, recovery, iwa-sage\n' >&2
    exit 4
    ;;
esac

block() {
  printf 'DEMO_EXECUTION=BLOCKED\nPRODUCT_ID=%s\nDEPENDENCY=%s\n' "$PRODUCT_ID" "$1" >&2
  exit 4
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE_CLI="${PHARO_QUEUE_CLI:-$REPO_ROOT/reference/nexinus_queue.py}"
LISTENER_CLI="${PHARO_LISTENER_CLI:-$REPO_ROOT/reference/phone_inbox_dedup.py}"
DEMO_PORT="${PHARO_DEMO_PORT:-7777}"
MAX_RETRY_WAIT_SECONDS="${PHARO_MAX_RETRY_WAIT_SECONDS:-40}"
LISTENER_PID=""
RUN_DIR=""

cleanup() {
  if [[ -n "$LISTENER_PID" ]] && kill -0 "$LISTENER_PID" 2>/dev/null; then
    kill "$LISTENER_PID" 2>/dev/null || true
    wait "$LISTENER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

require_env() {
  local name="$1"
  [[ -n "${!name:-}" ]] || block "set $name to an operator-supplied value"
}

require_env PHARO_PRODUCT_ADAPTER
require_env PHARO_RECIPIENT_PEER_ID
require_env PHARO_PEER_PUBLIC_KEY_B64
require_env PHARO_DEMO_ROOT

[[ "$PHARO_DEMO_ROOT" = /* ]] || block 'PHARO_DEMO_ROOT must be an absolute, operator-controlled output directory'
[[ "$DEMO_PORT" == "7777" ]] || block 'reference/phone_inbox_dedup.py is fixed to port 7777; do not substitute another port'
[[ "$MAX_RETRY_WAIT_SECONDS" =~ ^[0-9]+$ ]] || block 'PHARO_MAX_RETRY_WAIT_SECONDS must be a non-negative integer'
[[ -x "$PHARO_PRODUCT_ADAPTER" ]] || block "PHARO_PRODUCT_ADAPTER is not an executable real $PRODUCT_ID adapter"
[[ -f "$QUEUE_CLI" ]] || block "reference queue CLI not found at $QUEUE_CLI"
[[ -f "$LISTENER_CLI" ]] || block "reference listener not found at $LISTENER_CLI"
command -v python3 >/dev/null 2>&1 || block 'python3 is required to execute the repository reference implementation'

port_open() {
  python3 - "$1" <<'PY'
import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.2)
try:
    code = sock.connect_ex(("127.0.0.1", int(sys.argv[1])))
finally:
    sock.close()
raise SystemExit(0 if code == 0 else 1)
PY
}

# The stopped-listener assertion must be true before anything is enqueued. This
# prevents the demonstration from accidentally claiming an unavailable interval.
if port_open "$DEMO_PORT"; then
  block "127.0.0.1:$DEMO_PORT already has a listener; stop it so the queued-offline step can be observed"
fi

mkdir -p "$PHARO_DEMO_ROOT"
RUN_DIR="$(mktemp -d "$PHARO_DEMO_ROOT/${PRODUCT_ID}-offline-reference.XXXXXX")"
chmod 700 "$RUN_DIR"
RUN_HOME="$RUN_DIR/home"
mkdir -p "$RUN_HOME"
chmod 700 "$RUN_HOME"
PAYLOAD_JSON="$RUN_DIR/adapter-output.json"
PAYLOAD_FILE="$RUN_DIR/payload.txt"
QUEUE_DB="$RUN_HOME/.nexinus-queue.db"

# Proposed adapter interface. It is intentionally explicit that the product
# adapter, rather than this script, owns acquisition of the actual payload.
if ! "$PHARO_PRODUCT_ADAPTER" pharo-lapse-outbox \
    --product-id "$PRODUCT_ID" \
    --mode offline-reference-demo \
    --output "$PAYLOAD_JSON"; then
  block "the real $PRODUCT_ID adapter did not produce offline-demo adapter output"
fi

python3 - "$PAYLOAD_JSON" "$PRODUCT_ID" "$PAYLOAD_FILE" <<'PY'
import json
import sys
from pathlib import Path

source, expected_product, destination = map(Path, (sys.argv[1], sys.argv[2], sys.argv[3]))
# expected_product must remain a string; Path is only appropriate for paths.
expected_product = sys.argv[2]
try:
    value = json.loads(source.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"adapter output is not valid UTF-8 JSON: {exc}")
if not isinstance(value, dict) or set(value) != {"product_id", "body"}:
    raise SystemExit("adapter output must contain exactly product_id and body")
if value.get("product_id") != expected_product:
    raise SystemExit("adapter product_id does not match the selected product")
body = value.get("body")
if not isinstance(body, str) or not body or len(body) > 4096:
    raise SystemExit("adapter body must be a non-empty string of at most 4096 characters")
Path(destination).write_text(body, encoding="utf-8")
PY

queue() {
  HOME="$RUN_HOME" python3 "$QUEUE_CLI" "$@"
}

# Actual CLI calls from reference/nexinus_queue.py. The reference queue stores
# the pubkey but does not use it to sign/verify; the caller must still supply a
# real pinned value rather than this script fabricating one.
queue peer "$PHARO_RECIPIENT_PEER_ID" 127.0.0.1 "$DEMO_PORT" "$PHARO_PEER_PUBLIC_KEY_B64" \
  >"$RUN_DIR/peer-registration.txt"
queue add "$PHARO_RECIPIENT_PEER_ID" "$(cat "$PAYLOAD_FILE")" \
  >"$RUN_DIR/outbox-enqueue.txt"

# Listener is confirmed stopped. This one pass must leave the sole row pending
# after a retryable connection failure; the query below verifies observed state.
queue deliver --once >"$RUN_DIR/listener-stopped-delivery.txt" 2>&1
python3 - "$QUEUE_DB" >"$RUN_DIR/listener-stopped-observation.json" <<'PY'
import json
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
rows = conn.execute(
    "SELECT msg_id, state, attempts, next_attempt_at, last_error FROM outbox ORDER BY created_at"
).fetchall()
if len(rows) != 1:
    raise SystemExit(f"expected exactly one outbox row after enqueue, found {len(rows)}")
msg_id, state, attempts, next_attempt_at, last_error = rows[0]
if state != "pending" or attempts < 1 or not next_attempt_at:
    raise SystemExit("listener-stopped step did not leave a retry-scheduled pending row")
json.dump({
    "status": "listener-stopped-queue-observed",
    "msg_id": msg_id,
    "state": state,
    "attempts": attempts,
    "next_attempt_at": next_attempt_at,
    "last_error": last_error,
}, sys.stdout, sort_keys=True, indent=2)
print()
PY

# This is the provided reference listener, intentionally not a product runtime.
HOME="$RUN_HOME" python3 "$LISTENER_CLI" >"$RUN_DIR/listener-started.log" 2>&1 &
LISTENER_PID="$!"
for _ in $(seq 1 50); do
  if port_open "$DEMO_PORT"; then
    break
  fi
  sleep 0.1
done
if ! port_open "$DEMO_PORT"; then
  block "reference listener failed to start; see $RUN_DIR/listener-started.log"
fi

# The reference queue adds jitter to its first retry. Read its real scheduled
# time rather than bypassing the state machine or inventing a delivery result.
RETRY_WAIT_SECONDS="$(python3 - "$QUEUE_DB" <<'PY'
import math
import sqlite3
import sys
from datetime import datetime, timezone

conn = sqlite3.connect(sys.argv[1])
row = conn.execute("SELECT next_attempt_at FROM outbox").fetchone()
if row is None or not row[0]:
    raise SystemExit("pending outbox row has no next_attempt_at")
due = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
wait = max(0, math.ceil((due - datetime.now(timezone.utc)).total_seconds()) + 1)
print(wait)
PY
)"
if (( RETRY_WAIT_SECONDS > MAX_RETRY_WAIT_SECONDS )); then
  block "reference retry is due in ${RETRY_WAIT_SECONDS}s, exceeding PHARO_MAX_RETRY_WAIT_SECONDS=$MAX_RETRY_WAIT_SECONDS"
fi
sleep "$RETRY_WAIT_SECONDS"
queue deliver --once >"$RUN_DIR/listener-started-delivery.txt" 2>&1

# Construct a local reference observation only from data the real execution
# created. It intentionally makes no signed-v1.1, real-product, or deployment
# claim, and it does not include the raw application body.
python3 - "$QUEUE_DB" "$RUN_HOME/phone_inbox.db" "$PRODUCT_ID" "$RUN_DIR/local-reference-receipt.json" <<'PY'
import json
import sqlite3
import sys

queue_db, inbox_db, product_id, output = sys.argv[1:]
q = sqlite3.connect(queue_db)
rows = q.execute("""
    SELECT msg_id, created_at, peer_id, state, attempts, next_attempt_at,
           expires_at, last_error, acked_at, ack_json
    FROM outbox ORDER BY created_at
""").fetchall()
if len(rows) != 1:
    raise SystemExit(f"expected one outbox row after delivery, found {len(rows)}")
keys = ["msg_id", "created_at", "peer_id", "state", "attempts", "next_attempt_at",
        "expires_at", "last_error", "acked_at", "ack_json"]
outbox = dict(zip(keys, rows[0]))
if outbox["state"] != "acked" or not outbox["acked_at"]:
    raise SystemExit("listener-started step did not produce an acked reference outbox row")
try:
    ack = json.loads(outbox.pop("ack_json"))
except Exception as exc:
    raise SystemExit(f"reference queue stored invalid ack_json: {exc}")
if ack.get("msg_id") != outbox["msg_id"] or ack.get("received") is not True or not ack.get("sha256"):
    raise SystemExit("reference ack does not match the queued message or lacks required fields")
i = sqlite3.connect(inbox_db)
inbox = i.execute(
    "SELECT msg_id, received_at, sha256, ack_json FROM inbox WHERE msg_id=?", (outbox["msg_id"],)
).fetchone()
if inbox is None:
    raise SystemExit("reference listener did not persist the queued msg_id")
inbox_msg_id, received_at, body_sha256, inbox_ack_json = inbox
if inbox_msg_id != outbox["msg_id"] or body_sha256 != ack["sha256"]:
    raise SystemExit("reference inbox fields do not match the returned ack")
receipt = {
    "receipt_schema": "pharo-lapse-dimension-5-local-reference/0.1",
    "execution_status": "LOCAL_REFERENCE_DEMO_ONLY",
    "product_id": product_id,
    "outbox": outbox,
    "reference_listener_ack": {
        "received": ack.get("received"),
        "msg_id": ack.get("msg_id"),
        "sha256": ack.get("sha256"),
        "new": ack.get("new"),
    },
    "reference_inbox": {
        "msg_id": inbox_msg_id,
        "received_at": received_at,
        "body_sha256": body_sha256,
        "cached_ack_matches": json.loads(inbox_ack_json) == ack,
    },
    "limitations": [
        "Local loopback reference queue/listener only; not a live product runtime or deployment.",
        "Reference listener ack is unsigned and reference queue does not verify an ack signature.",
        "This is not a PHARO-LAPSE-1.1.0 receipt, signed transport proof, or application-processing proof.",
        "Raw adapter body is intentionally omitted from this observation."
    ]
}
with open(output, "w", encoding="utf-8") as stream:
    json.dump(receipt, stream, sort_keys=True, indent=2)
    stream.write("\n")
PY

printf 'DEMO_EXECUTION=LOCAL_REFERENCE_DEMO_COMPLETED\nPRODUCT_ID=%s\nOUTPUT_DIR=%s\nRECEIPT=%s\n' \
  "$PRODUCT_ID" "$RUN_DIR" "$RUN_DIR/local-reference-receipt.json"
