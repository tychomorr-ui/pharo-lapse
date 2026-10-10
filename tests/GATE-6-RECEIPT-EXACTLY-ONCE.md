# NEXINUS — GATE 6 RECEIPT
## Exactly-once delivery over WAN-disconnected WireGuard

**Date:** 2026-10-09
**Result:** PASS

## Dedup sequence
1. Queue 2 messages, deliver once
   - 0dc54651-e1c0-494e-9a0c-0aeacfe0b00f -> NEW, sha 52ce7e30...
   - 2bb0ace2-ca1a-4024-a416-e86b69ac70d2 -> NEW, sha a1893a35...
2. Force redelivery of the same msg_ids
   - 0dc54651-... -> DUP, same sha 52ce7e30...
   - 2bb0ace2-... -> DUP, same sha a1893a35...
3. Receiver returned the SAME ack both times, did not process twice

## What this proves
- Receiver maintains persistent inbox (SQLite)
- msg_id is the dedup key
- Duplicate deliveries return the cached ack, not a re-processed one
- Body SHA-256 is stable across retries
- Exactly-once delivery semantics hold across the tunnel

## Combined with Gate 5
- Sender: durable outbox, retry, crash recovery, restart survival
- Receiver: persistent inbox, msg_id dedup, ack replay
- Together: store-and-forward with exactly-once semantics over a
  self-hosted encrypted overlay on a WAN-disconnected network

## Limitations (honest)
- Two devices, same physical location
- WAN-disconnected but not radio-silent
- Both directions are Ed25519 signed (probe layer)
- Not yet tested: multihop, geographically distributed peers

## Gate Ladder status
- Gate 3: HTTP over tunnel, no internet  — PASS
- Gate 4: Signed envelope + signed ack  — PASS
- Gate 5: Store-and-forward + restart  — PASS
- Gate 6: Exactly-once delivery         — PASS
- Gate 7: Multihop relay                — NOT STARTED
- Gate 8: Geographically distributed    — NOT STARTED
