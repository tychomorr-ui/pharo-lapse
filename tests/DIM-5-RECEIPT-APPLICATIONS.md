# PHARO-LAPSE DIMENSION 5 RECEIPT
## Application-layer integration flows and guarded offline demos

**Date:** 11 October 2026
**Status:** **BLOCKED for product-demo execution; static artifacts and guardrails validated**
**Rule set boundary:** `PHARO-LAPSE-1.1.0` specifies signed receipt requirements. The supplied offline runner deliberately uses the repository's minimal reference queue/listener and must not be treated as a v1.1 execution harness.

## Delivered artifacts

| Product | Publishable flow | Executable product entry point | Execution status |
|---|---|---|---|
| PD Pro | `applications/pd-pro/INTEGRATION-FLOW.md` | `applications/pd-pro/offline-demo.sh` | **BLOCKED** — no real adapter or authorized runtime is available. |
| Task Force Pro | `applications/task-force-pro/INTEGRATION-FLOW.md` | `applications/task-force-pro/offline-demo.sh` | **BLOCKED** — no real adapter or authorized runtime is available. |
| Recovery | `applications/recovery/INTEGRATION-FLOW.md` | `applications/recovery/offline-demo.sh` | **BLOCKED** — no real adapter or authorized runtime is available. |
| IWA Sage | `applications/iwa-sage/INTEGRATION-FLOW.md` | `applications/iwa-sage/offline-demo.sh` | **BLOCKED** — no real adapter or authorized runtime is available. |

Shared artifacts:

- `applications/adapter-output.schema.json` — proposed, explicit adapter-output boundary. It is **not** an assertion of an existing product API or CLI.
- `applications/run-offline-reference-demo.sh` — executable guarded runner used by the four product wrappers.

## Integration contract and flow boundary

Each flow documents these real repository calls and steps:

1. An **operator-supplied real product adapter** must emit the application body; the scripts never synthesize it.
2. The actual reference CLI call `python3 reference/nexinus_queue.py add "$PHARO_RECIPIENT_PEER_ID" "$BODY"` writes the local durable outbox row.
3. With the reference listener confirmed stopped, `deliver --once` must leave the one row `pending` with an incremented attempt and scheduled retry.
4. The repository reference listener is then started on loopback; after the actual retry deadline, another `deliver --once` may produce a local `acked` row.
5. Only after successful local execution, the runner writes a runtime-generated `local-reference-receipt.json` containing outbox, unsigned listener-ack, and inbox fields. It excludes the raw application body.

The reference implementation limitations are material: `reference/nexinus_queue.py` builds a minimal envelope and does not verify an ack signature; `reference/phone_inbox_dedup.py` returns an unsigned ack and does not verify signatures or CIDs. A resulting local observation cannot establish a signed receipt, a v1.1 delivery, a real product action, a deployment, telemetry, or a live endpoint result.

## Receipt fields documented

| Category | Fields |
|---|---|
| Reference outbox observation | `msg_id`, `created_at`, `peer_id`, `state`, `attempts`, `next_attempt_at`, `expires_at`, `last_error`, `acked_at`, `ack_json` |
| Reference listener ack | `received`, `msg_id`, `sha256`, `new` |
| Reference inbox observation | `msg_id`, `received_at`, `peer_id`, `body_sha256` |
| Required signed v1.1 outbound receipt — **not emitted by this demo** | `receipt_id`, `msg_id`, sender/recipient IDs, `input_hash`, `origin_cid`, `state_hash`, `rule_set_version`, `authority_state`, `model_inference`, `external_ai`, `phase`, `lapse`, `route_history`, `max_hops`, `result_state`, `sig` |

## Validation completed

The following static and guarded checks completed in this sandbox:

```text
python3 -m json.tool applications/adapter-output.schema.json
bash -n applications/run-offline-reference-demo.sh applications/*/offline-demo.sh
Python structural check: four Markdown flows contain truth boundary, adapter boundary,
  listener-stopped/listener-started steps, receipt fields, BLOCKED status, and executable wrappers
applications/{pd-pro,task-force-pro,recovery,iwa-sage}/offline-demo.sh
  -> exit 4 and emit DEMO_EXECUTION=BLOCKED when no real adapter is supplied
git diff --check
```

No adapter was supplied to a runner. Consequently, **no listener was started, no payload was created, no peer key or peer ID was generated, no message was queued, no message ID was produced, no delivery was attempted, and no runtime receipt exists.**

## LIVE / PENDING / BLOCKED

| Item | State | Evidence / dependency |
|---|---|---|
| Four publishable flows, four executable wrappers, shared guarded runner, and adapter schema | LIVE as repository artifacts | Paths above; static checks passed. This does not imply a live product runtime. |
| Guardrail on missing real adapter | LIVE as a negative-path check | Each wrapper returned `DEMO_EXECUTION=BLOCKED` with exit code 4. |
| PD Pro offline reference execution | BLOCKED | Requires an operator-supplied executable PD Pro adapter, genuine payload under authority, pinned recipient identity/key, and authorization. |
| Task Force Pro offline reference execution | BLOCKED | Requires an operator-supplied executable Task Force Pro adapter, genuine payload under authority, pinned recipient identity/key, and authorization. |
| Recovery offline reference execution | BLOCKED | Requires an operator-supplied executable Recovery adapter, genuine payload under authority, pinned recipient identity/key, and authorization. |
| IWA Sage offline reference execution | BLOCKED | Requires an operator-supplied executable IWA Sage adapter, genuine payload under authority, pinned recipient identity/key, and authorization. |
| Signed v1.1 receipt / application acknowledgement | PENDING | Requires a conforming signed v1.1 sender and recipient listener with pinned keys, phase/lapse/CID checks, and an authorized real endpoint. |
| Deployment, live telemetry, contacts, submissions, contracts, or product results | BLOCKED | None were provided or performed in this sandbox; none are claimed. |

## Boundary

This receipt records **files and static/guardrail validation only**. It does not replace Gate 3–6 evidence and does not alter those receipts, the v1.0/v1.1 specifications, or Cryptochrometer code.
