# Project Reclaim → Pharo-Lapse Integration

**Status:** READY for sanitized v1 reference events; live signed delivery remains PENDING.

## Correct project name

This integration is for **Project Reclaim on Pharo-Lapse**. It is not a Feral Labs integration.

## Intended flow

```text
Project Reclaim event
  -> operator-approved event export
  -> deterministic adapter serialization
  -> signed Pharo-Lapse origin envelope
  -> local durable outbox
  -> WireGuard overlay peer
  -> signed acknowledgment
  -> exactly-once recipient deduplication
```

## v1 reference event contract

The first reference event is deliberately non-sensitive and contains no location field:

```json
{
  "event_id": "PR-TEST-001",
  "event_type": "status",
  "created_at": "2026-10-16T16:00:00Z",
  "priority": "routine",
  "origin": "project-reclaim",
  "message": "Project Reclaim reference status test"
}
```

Allowed `event_type` values are `status`, `fire`, `medical`, `supply`, and `outage`.
Allowed priorities are `routine`, `urgent`, and `critical`. The operator must set
`PROJECT_RECLAIM_OPERATOR_APPROVAL=approved` before an event is serialized.

Serialization is UTF-8 JSON with sorted keys, compact separators, and the schema
marker `PROJECT-RECLAIM-EVENT/1`.

## Current verified boundary

The repository already contains the canonical peer entry `project-reclaim` in
`ecosystem/peer-manifest.json`. The intended overlay address is `10.9.0.5`
with SFO2 hub `10.9.0.1`. These values are configuration inputs, not proof of
a current handshake or application delivery.

The repository also contains the signed multi-hop implementation:

- `reference/envelope_v3.py`
- `reference/forward_signed.py`
- `reference/tests/test_signed_multihop.py`

## Remaining production blocker

The v1 reference schema is implemented for sanitized testing. It is not yet an
authoritative production schema. Production use remains blocked until all of the
following are supplied:

1. Project Reclaim owner approval of the v1 schema or a replacement schema;
2. configured recipient peer ID, overlay address, port, and pinned Ed25519 key;
3. production queue and signed-envelope integration;
4. a live signed delivery and acknowledgment receipt.

`add-to-pharo-lapse.sh` intentionally uses the legacy unsigned reference SQLite
queue and reports that limitation. It must not be described as signed production
transport.

## What this package does not claim

- It does not claim that the Project Reclaim WireGuard handshake is live.
- It does not claim that TCP 7777 is reachable.
- It does not claim that Project Reclaim application events have been delivered.
- It does not create or copy private keys.
- It does not modify the protocol specification.
