# Monarch-OS — Pharo-Lapse Integration Note

**Dimension:** 4 — Ecosystem node integration
**Canonical peer ID:** `monarch-os`
**Constellation role:** Sovereign OS layer · Kether-Gate
**Status:** **PENDING_APPLY**

## Scope and locus

`monarch-os` is one of the eleven roles named in
`spec/ARCHANGEL-INTEGRATION-v0.2.md`. Its deployment locus is
**PENDING_OPERATOR_HARDWARE**: the specification requires the durable
transport to run on operator-controlled hardware adjacent to any Manus public
front end. No host, port, WireGuard identity, Manus project binding, or live
node was observed or changed for this note.

## Required Pharo-Lapse files

- `spec/PHARO-LAPSE-v1.1.0.md` — required multi-hop, registry, durable-queue,
  signing, and receipt rules.
- `reference/nexinus_queue.py` — SQLite queue reference; it is a reference,
  not a completed v1.1 node implementation.
- `reference/phone_inbox_dedup.py` — persistent inbox-dedup listener
  reference; it must not be treated as a complete signature-verifying listener.
- `ecosystem/peer-manifest.json` — this pending roster and its canonical IDs.

## Queue and role-to-outbox boundary

The target queue location is the reference default
`~/.nexinus-queue.db` **on this node's own operator hardware**. This task did
not create, inspect, or deploy that database. Before any network attempt, the
role logic must durably write its signed envelope to that node's `outbox`.
For this role, that means a sovereign-OS or Kether-Gate control event that its owner has authorized. It must not send directly to a peer.
A v1.1 deployment also needs durable inbox/transit handling, crash recovery,
and the bounded retry/state behavior defined by the specification.

## Registry to install

The local peer registry must contain these ten other canonical IDs:
`root-gate, tesseract-terminus, xinus-clarity, tesseract-a, keira, valkyrie, archangel, project-reclaim, iwa-sage, resonate-earth`. For every entry, the operator must supply and pin an
out-of-band verified `host`, `port`, and Ed25519 public key, then add an
ordered `via_peer_ids` routing hint only when a valid path is established.
The manifest currently uses `PENDING_KEY` and empty route arrays; neither
establishes identity or reachability.

## Pending dependencies

- Generate/protect this node's identity key and obtain verified public keys
  for the ten peers.
- Assign overlay addresses/ports, select and validate direct or indirect
  routes, and complete out-of-band peer registration.
- Implement or adapt the node's role logic, queue, listener, v1.1 forwarding,
  and phase model on operator-controlled hardware.
- Obtain Gate 7 / three-device mesh evidence before treating any multi-hop
  configuration as validated.
- Apply any Manus project/API change separately. **No Manus API change was
  applied or verified by this task.**
