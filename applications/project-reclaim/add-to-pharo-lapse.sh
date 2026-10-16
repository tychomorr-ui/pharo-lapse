#!/usr/bin/env bash
# Project Reclaim -> Pharo-Lapse reference SQLite queue bridge.
# This is a local unsigned reference path, not signed production delivery.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${PHARO_PYTHON:-python3}"
ADAPTER="$ROOT/applications/project-reclaim/adapter-template.py"
QUEUE="$ROOT/reference/nexinus_queue.py"

required=(PROJECT_RECLAIM_EVENT_FILE PHARO_RECIPIENT_PEER_ID PHARO_RECIPIENT_HOST PHARO_RECIPIENT_PORT PHARO_PEER_PUBLIC_KEY_B64 PHARO_QUEUE_HOME)
for name in "${required[@]}"; do
  [[ -n "${!name:-}" ]] || { echo "PROJECT_RECLAIM_REFERENCE=BLOCKED"; echo "DEPENDENCY=set $name"; exit 4; }
done
[[ "$PHARO_QUEUE_HOME" = /* ]] || { echo "PROJECT_RECLAIM_REFERENCE=BLOCKED"; echo "DEPENDENCY=PHARO_QUEUE_HOME must be absolute"; exit 4; }
[[ -f "$PROJECT_RECLAIM_EVENT_FILE" ]] || { echo "PROJECT_RECLAIM_REFERENCE=BLOCKED"; echo "DEPENDENCY=event file does not exist"; exit 4; }
[[ "$PHARO_RECIPIENT_PORT" =~ ^[0-9]+$ ]] || { echo "PROJECT_RECLAIM_REFERENCE=BLOCKED"; echo "DEPENDENCY=recipient port must be numeric"; exit 4; }

run_dir="$(mktemp -d)"
trap 'rm -rf "$run_dir"' EXIT
export PROJECT_RECLAIM_OPERATOR_APPROVAL="${PROJECT_RECLAIM_OPERATOR_APPROVAL:-approved}"
"$PYTHON" "$ADAPTER" pharo-lapse-outbox --output "$run_dir/output.json"
body="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["body"])' "$run_dir/output.json")"

mkdir -p "$PHARO_QUEUE_HOME"
chmod 700 "$PHARO_QUEUE_HOME"
HOME="$PHARO_QUEUE_HOME" "$PYTHON" "$QUEUE" peer \
  "$PHARO_RECIPIENT_PEER_ID" "$PHARO_RECIPIENT_HOST" "$PHARO_RECIPIENT_PORT" "$PHARO_PEER_PUBLIC_KEY_B64"
HOME="$PHARO_QUEUE_HOME" "$PYTHON" "$QUEUE" add "$PHARO_RECIPIENT_PEER_ID" "$body"

printf '%s\n' \
  'PROJECT_RECLAIM_REFERENCE=LOCAL_OUTBOX_ENQUEUED' \
  "RECIPIENT=$PHARO_RECIPIENT_PEER_ID" \
  "QUEUE_HOME=$PHARO_QUEUE_HOME" \
  'DELIVERY=NOT_ATTEMPTED' \
  'LIMITATION=legacy unsigned reference queue; signed production path still required'
