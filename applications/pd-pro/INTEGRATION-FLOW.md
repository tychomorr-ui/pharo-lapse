# PD Pro — Pharo-Lapse Application Integration Flow

**Dimension:** 5 — Application layer
**Status:** **BLOCKED — no PD Pro runtime, adapter, endpoint, or pinned peer configuration is available in this repository or sandbox.**
**Flow type:** Direct, single-hop **offline reference demonstration**; not a live deployment and not a v1.1 conformance claim.

## Truth boundary

This repository contains no PD Pro source code, product API documentation, product CLI, running service, recipient endpoint, or PD Pro adapter. Therefore this document **does not assert a PD Pro event name, data model, side effect, API route, contact, deployment, message ID, delivery, or receipt**.

The only usable outbox command present in this repository is the reference queue CLI:

```bash
python3 /home/ubuntu/pharo-lapse/reference/nexinus_queue.py add "$PHARO_RECIPIENT_PEER_ID" "$BODY"
```

That call creates a local SQLite outbox row. It is a real call in `reference/nexinus_queue.py`; it is **not** a PD Pro API call and, as currently implemented, does not produce a signed v1.1 envelope. A real PD Pro adapter is required to supply `BODY` at execution time.

## Required adapter boundary

The operator supplies an executable in `PHARO_PRODUCT_ADAPTER`. For this integration boundary, it must support the proposed invocation below and write output conforming to [`../adapter-output.schema.json`](../adapter-output.schema.json):

```bash
"$PHARO_PRODUCT_ADAPTER" pharo-lapse-outbox \
  --product-id pd-pro \
  --mode offline-reference-demo \
  --output "$PAYLOAD_JSON"
```

Required output properties are `product_id: "pd-pro"` and a non-empty `body` of at most 4096 characters. This is a **new adapter contract for the integration**, not a claim about an existing PD Pro command. The adapter must obtain any genuine application payload under the operator's authority and must not fabricate one.

## Repeatable flow

| Step | Action | Observable local state | Boundary |
|---|---|---|---|
| 1. Prepare | Real PD Pro adapter writes its validated payload JSON. | Payload JSON exists only if the adapter succeeds. | **BLOCKED** until a real adapter is supplied. |
| 2. Register test peer | `nexinus_queue.py peer "$PHARO_RECIPIENT_PEER_ID" 127.0.0.1 7777 "$PHARO_PEER_PUBLIC_KEY_B64"` writes the peer row. | Local `peers` row. | Loopback reference only; no production peer is asserted. |
| 3. Real outbox call | `nexinus_queue.py add "$PHARO_RECIPIENT_PEER_ID" "$BODY"`. | A locally generated `msg_id` and outbox row in `pending`. | The script never preselects or prints a message ID before a real execution. |
| 4. Listener stopped | With no process listening on `127.0.0.1:7777`, `nexinus_queue.py deliver --once` is run. | Reference queue records a retryable connection error, increments `attempts`, and leaves the row `pending` with `next_attempt_at`. | This demonstrates local queue behavior only. |
| 5. Listener started | The repository's `reference/phone_inbox_dedup.py` is started on `127.0.0.1:7777`; after the recorded retry time, `deliver --once` is run again. | Local row becomes `acked` only if the reference listener returns HTTP 200; inbox has one `msg_id` row. | Not a PD Pro listener, network, or deployment. |
| 6. Capture | The script emits `local-reference-receipt.json` from SQLite and returned ack fields. | Runtime-generated evidence stays in the run directory. | It is explicitly not a signed protocol receipt or live-product result. |

## Receipt fields and limits

| Source | Capturable fields in a real offline execution | What they mean / do not mean |
|---|---|---|
| Reference outbox row | `msg_id`, `created_at`, `peer_id`, `state`, `attempts`, `next_attempt_at`, `expires_at`, `last_error`, `acked_at`, `ack_json` | Queue bookkeeping from `reference/nexinus_queue.py`; not a PD Pro business receipt. |
| Reference listener ack | `received`, `msg_id`, `sha256`, `new` | The listener implementation returns this unsigned JSON and caches it by `msg_id`; it is not an Ed25519-signed v1.1 ack. |
| Reference inbox row | `msg_id`, `received_at`, `peer_id`, `body_sha256` | Confirms the local reference listener stored one row; it does not prove application processing. |
| Required v1.1 outbound receipt (not produced by this demo) | `receipt_id`, `msg_id`, sender/recipient IDs, `input_hash`, `origin_cid`, `state_hash`, `rule_set_version`, `authority_state`, `model_inference`, `external_ai`, `phase`, `lapse`, `route_history`, `max_hops`, `result_state`, `sig` | Requires a conforming signed v1.1 adapter/transport and a real pinned recipient. **PENDING.** |

> `reference/nexinus_queue.py` only creates a minimal `msg_id`/body envelope and accepts JSON ack data without signature verification. `reference/phone_inbox_dedup.py` does not verify signatures or CIDs. The supplied demo must not be represented as a signed, hardware-bound, or live PD Pro delivery.

## Run only with a real adapter

```bash
PHARO_PRODUCT_ADAPTER=/absolute/path/to/real-pd-pro-adapter \
PHARO_RECIPIENT_PEER_ID=operator-configured-recipient \
PHARO_PEER_PUBLIC_KEY_B64=operator-supplied-pinned-key \
PHARO_DEMO_ROOT=/absolute/path/to/operator-controlled-output \
/home/ubuntu/pharo-lapse/applications/pd-pro/offline-demo.sh
```

The wrapper delegates to `applications/run-offline-reference-demo.sh pd-pro`. It exits **BLOCKED** rather than generating payloads, keys, peer IDs, listeners, message IDs, or results when its real-adapter prerequisites are absent.

## Status

- **LIVE:** No PD Pro runtime or live delivery is claimed.
- **PENDING:** Operator review of the proposed adapter contract; a conforming signed v1.1 transport; real peer registration and authorization.
- **BLOCKED:** A real PD Pro adapter, operator-supplied pinned recipient identity, and an authorized runtime are unavailable here.
