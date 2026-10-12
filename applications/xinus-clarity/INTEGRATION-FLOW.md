# XinUS Clarity → Pharo-Lapse bridge

The bridge is [`add-to-pharo-lapse.sh`](add-to-pharo-lapse.sh). It accepts a real, operator-approved XinUS Clarity export as a UTF-8 text file, registers an explicitly supplied recipient in the local reference queue, and enqueues the payload.

It does **not** call a XinUS API because no XinUS API contract or runtime is present in this repository. It does **not** create a payload, recipient, public key, message ID, signed v1.1 envelope, delivery result, or receipt.

## Required inputs

```bash
export XINUS_CLARITY_PAYLOAD_FILE=/absolute/path/to/operator-approved-payload.txt
export PHARO_RECIPIENT_PEER_ID=operator-configured-recipient
export PHARO_RECIPIENT_HOST=operator-configured-overlay-host
export PHARO_RECIPIENT_PORT=7777
export PHARO_PEER_PUBLIC_KEY_B64=operator-supplied-pinned-key
export PHARO_QUEUE_HOME=/absolute/path/to/operator-controlled/queue-home
```

Run:

```bash
applications/xinus-clarity/add-to-pharo-lapse.sh
```

The script uses `reference/nexinus_queue.py` and reports `LOCAL_OUTBOX_ENQUEUED` only after the local queue command succeeds. It deliberately reports `DELIVERY=NOT_ATTEMPTED`.

## Important boundary

The reference queue stores the peer row and a local outbox row, but it does not produce or verify the complete PHARO-LAPSE v1.1 signed envelope. Do not represent this bridge as a live XinUS integration, signed transport, hardware-bound identity, or delivery proof.

A production XinUS integration still requires an approved XinUS event/export contract, v1.1-compliant adapter and transport, pinned key-management procedure, authorized recipient, listener, test environment, and independent validation.
