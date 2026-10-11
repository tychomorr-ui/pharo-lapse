# Pharo-Lapse Protocol

A store-and-forward message delivery protocol for sovereign devices operating over intermittent or unavailable network infrastructure.

Signed end-to-end delivery. Exactly-once semantics. Durable queueing on both endpoints. No public internet. No cloud brokers. No certificate authorities. No third-party service.

## What's Here

- spec/PHARO-LAPSE-v1.0.0.md — the complete protocol specification
- spec/ARCHANGEL-INTEGRATION-v0.2.md — integration design for an 11-node constellation
- reference/nexinus_queue.py — the durable queue
- reference/phone_inbox_dedup.py — recipient-side listener with dedup
- reference/NEXINUS-WG-SIGNED-PROBE.py — signed envelope exchange over WireGuard
- tests/ — four verified test receipts

## Verified

All four test classes pass on real hardware (Chromebook Linux + Android phone) over a WAN-disconnected WireGuard overlay:

- Gate 3 — HTTP transport with no internet
- Gate 4 — Signed envelope and signed ack
- Gate 5 — Store-and-forward with crash recovery
- Gate 6 — Exactly-once delivery

## The Four Rules

1. Identity is hardware-bound
2. Every message is signed and content-addressed
3. Every peer holds its own queue
4. Dedup is by msg_id

## Bitcoin Anchor

The v1.0.0 commit hash is anchored to Bitcoin block 970,786 via OpenTimestamps.

- Block height: 970,786
- Target: pharo-lapse-commit.txt
- Proof: pharo-lapse-commit.txt.ots

Verify: ots verify pharo-lapse-commit.txt.ots pharo-lapse-commit.txt

---

Author: Tyler Morris, Nexinus RI Systems LLC
Date: 9-10 October 2026
