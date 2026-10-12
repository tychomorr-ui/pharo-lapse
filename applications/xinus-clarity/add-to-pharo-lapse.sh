#!/usr/bin/env bash
# XinUS Clarity -> Pharo-Lapse local outbox bridge.
#
# This script does not call a XinUS API and does not invent an event. The
# XinUS suite must first export an operator-approved, non-sensitive payload to
# XINUS_CLARITY_PAYLOAD_FILE. This uses the repository's reference SQLite queue
# only; it is not signed v1.1 transport or live delivery.
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QUEUE_CLI="${PHARO_QUEUE_CLI:-$REPO_ROOT/reference/nexinus_queue.py}"

block() {
  printf 'XINUS_PHARO_LAPSE=BLOCKED\nDEPENDENCY=%s\n' "$1" >&2
  exit 4
}

require_env() {
  local name="$1"
  [[ -n "${!name:-}" ]] || block "set $name to an operator-supplied value"
}

require_env XINUS_CLARITY_PAYLOAD_FILE
require_env PHARO_RECIPIENT_PEER_ID
require_env PHARO_RECIPIENT_HOST
require_env PHARO_RECIPIENT_PORT
require_env PHARO_PEER_PUBLIC_KEY_B64
require_env PHARO_QUEUE_HOME

[[ -f "$XINUS_CLARITY_PAYLOAD_FILE" ]] || block "payload file does not exist"
[[ "$PHARO_QUEUE_HOME" = /* ]] || block "PHARO_QUEUE_HOME must be an absolute operator-controlled directory"
[[ "$PHARO_RECIPIENT_PORT" =~ ^[0-9]+$ ]] || block "PHARO_RECIPIENT_PORT must be numeric"
[[ -f "$QUEUE_CLI" ]] || block "reference queue CLI not found at $QUEUE_CLI"

body_bytes="$(wc -c < "$XINUS_CLARITY_PAYLOAD_FILE")"
(( body_bytes > 0 && body_bytes <= 16384 )) || block "payload file must be 1-16384 bytes"

# Reject NUL bytes and invalid UTF-8 before passing the body to the queue CLI.
python3 - "$XINUS_CLARITY_PAYLOAD_FILE" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
data = p.read_bytes()
if b'\x00' in data:
    raise SystemExit('BLOCKED: payload contains a NUL byte')
data.decode('utf-8')
PY

mkdir -p "$PHARO_QUEUE_HOME"
chmod 700 "$PHARO_QUEUE_HOME"

# These are explicit operator-provided values. The reference queue stores the
# peer row locally but does not sign or verify v1.1 envelopes.
HOME="$PHARO_QUEUE_HOME" python3 "$QUEUE_CLI" peer \
  "$PHARO_RECIPIENT_PEER_ID" \
  "$PHARO_RECIPIENT_HOST" \
  "$PHARO_RECIPIENT_PORT" \
  "$PHARO_PEER_PUBLIC_KEY_B64"

# The body is read from the real XinUS export; no message ID is fabricated here.
HOME="$PHARO_QUEUE_HOME" python3 "$QUEUE_CLI" add \
  "$PHARO_RECIPIENT_PEER_ID" \
  "$(cat "$XINUS_CLARITY_PAYLOAD_FILE")"

printf '%s\n' \
  'XINUS_PHARO_LAPSE=LOCAL_OUTBOX_ENQUEUED' \
  "PRODUCT_ID=xinus-clarity" \
  "QUEUE_HOME=$PHARO_QUEUE_HOME" \
  "RECIPIENT_PEER_ID=$PHARO_RECIPIENT_PEER_ID" \
  'DELIVERY=NOT_ATTEMPTED' \
  'LIMITATION=reference SQLite queue; unsigned/non-v1.1 local operation'
