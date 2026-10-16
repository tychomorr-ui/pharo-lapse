# Project Reclaim → Pharo-Lapse Integration

**Status:** PENDING — transport identity and application contract are not yet verified.

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

## Current verified boundary

The repository already contains the canonical peer entry `project-reclaim` in
`ecosystem/peer-manifest.json`. The intended overlay address is `10.9.0.5`
with SFO2 hub `10.9.0.1`. These values are configuration inputs, not proof of
a current handshake or application delivery.

The repository also contains the signed multi-hop implementation:

- `reference/envelope_v3.py`
- `reference/forward_signed.py`
- `reference/tests/test_signed_multihop.py`

## Deliberate blocker

Project Reclaim's authoritative application event schema has not been provided.
The adapter must not invent fields, identifiers, timestamps, severity values,
or payload semantics. `adapter-template.py` therefore validates that an event
file is present, then exits `BLOCKED` until all of the following are supplied:

1. authoritative event schema and version;
2. deterministic serialization rules;
3. operator approval mechanism;
4. configured recipient peer ID, overlay address, port, and pinned Ed25519 key;
5. production queue and signed-envelope integration;
6. a live signed delivery and acknowledgment receipt.

## What this package does not claim

- It does not claim that the Project Reclaim WireGuard handshake is live.
- It does not claim that TCP 7777 is reachable.
- It does not claim that Project Reclaim application events have been delivered.
- It does not create or copy private keys.
- It does not modify the protocol specification.

## Required next implementation step

Provide one real, non-sensitive Project Reclaim event example and its authoritative
schema. Then implement the adapter serializer and test it against the shared
Pharo-Lapse output contract before enabling any network delivery.
