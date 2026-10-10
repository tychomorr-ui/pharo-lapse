# Archangel Integration — Pharo-Lapse as Transport Layer (v0.2)

**Status:** Design document, not yet implemented
**Depends on:** Gate 7 (three-device mesh test)
**Author:** Tyler Morris, Nexinus RI Systems LLC
**Date:** 10 October 2026

---

## The Constellation

The 11-node mesh is a constellation of role-assigned nodes. Each node has one job. Each node runs the same transport. The roles are different. The transport is the same.

| Node | Role |
|------|------|
| Root-Gate | Identity anchor · front door |
| Tesseract-Terminus | Provenance · anchoring |
| XinUS-Clarity | Flagship application layer |
| Monarch-OS | Sovereign OS layer · Kether-Gate |
| Tesseract-A | Recovery Mirror |
| KEIRA | Intelligence · truth analysis |
| Valkyrie | Adjudication entity |
| Archangel | Control plane |
| Project Reclaim | Field activation |
| IWA Sage | Community wellness |
| Resonate Earth | Public front door |

Archangel is one node. It has a control-plane role. It is not a hub. It does not route for other nodes. It performs its role, runs its own queue, and uses Pharo-Lapse to exchange signed envelopes with the other 10 nodes.

---

## What Runs on Each Node

Every node runs:

1. Its own role logic (Archangel logic, Valkyrie logic, etc.)
2. The Pharo-Lapse transport (outbox, inbox, delivery loop, listener, dedup)
3. Its own WireGuard overlay identity
4. Its own peer registry (the other 10 nodes)
5. Its own phase model (DAY / NIGHT / TWILIGHT)

The role logic differs. The transport is identical.

---

## Where the Transport Runs

Manus-hosted projects are static front-ends on Cloudflare Workers. They cannot run a long-lived listener or hold durable state.

The transport runs on real hardware next to the Manus front-end:

- Chromebook Penguin containers
- Small always-on devices (Raspberry Pi, mini-PC)
- VPS instances the operator controls

The Manus URL remains the public face. The queue runs on the operator's hardware.

Two patterns are valid:

**Pattern A — Front-end + local queue.** Manus URL serves the public face. A Penguin/machine process on the same overlay runs the Pharo-Lapse queue. The front-end reads from the queue.

**Pattern B — Hardware-only node.** A machine acts as the node. No public Manus URL. All logic — role logic and transport — runs on the machine.

Either pattern works. Both are peers.

---

## Interconnection

Full mesh connectivity across 11 nodes requires 55 pairwise tunnels. Impractical to maintain by hand.

Correct model is partial mesh with indirect paths:

- Node A has direct tunnels to B, C, D
- Node B has direct tunnels to E, F, G
- Node A sends to F. A has no tunnel to F. A sends to B. B forwards to F.

The relay is not designated. It emerges from the path.

For this to work, the peers table records indirect paths:

| peer_id | reachable_directly | via_peer_ids |

When Node A sends to Node F, it picks B from the via list. It sends to B with recipient = F. B checks its registry, sees F direct, delivers.

Envelope is signed by A. B cannot forge it. End-to-end receipt is between A and F. B is transparent.

---

## Protocol Extensions Required

Current Pharo-Lapse v1.0.0 does not support multi-hop. The following extensions are required.

### Envelope extensions

- route_history — array of peer_ids the envelope has traversed
- max_hops — integer, maximum number of relays allowed

### Registry extensions

- via_peer_ids — array of peer_ids through which this peer is reachable

### Delivery algorithm extensions

- Accept a via parameter for the next-hop peer
- Append own peer_id to route_history before forwarding
- Reject envelopes whose route_history already contains the local peer_id
- Reject envelopes where route_history.length >= max_hops

Backward-compatible. A v1.0.0 node treats the new fields as opaque. A v1.1.0 node uses them for multi-hop routing.

---

## Per-Node Integration

Each Manus project is updated separately. Steps are identical for every node.

1. Add the peer registry (10 other nodes' peer_ids, hosts, ports, public keys)
2. Add the outbox and inbox (SQLite, same schema)
3. Add the listener (local process, or part of the node)
4. Add the sender (role logic writes to outbox)
5. Pin each peer's public key
6. Add the phase model
7. Register the node with the other 10 peers (out of band)

The work is repetition, not invention. Same code, 11 times.

---

## Current Status

Two devices run Pharo-Lapse today. Gate 7 (three-device mesh) is next.

Scaling to 11 happens after Gate 7. Replicating a verified pattern is mechanical.

---

**End of Document**
