# NEXINUS — GATE 5 RECEIPT
## Pharo gap store-and-forward over WAN-disconnected WireGuard

**Date:** 2026-10-09
**Result:** PASS

## Sequence proven
1. Queue 3 messages while receiver is offline
2. All 3 attempts time out (receiver unreachable)
3. Messages persist in `pending` state on disk
4. Process killed completely (Terminal app closed)
5. Process restarted
6. State survives: `pending: 3`
7. Receiver brought online, tunnel re-established
8. Delivery resumes automatically
9. All 3 messages delivered and `acked`

## Message IDs
- ec4a0373-6b9b-47f6-b6be-a23a65abe820
- 5a2fb1e5-1a40-40f5-b617-98f00d9ebad9
- 52c4545b-2aed-402f-b6d5-565063ac9c6d

## What this proves
- Durable queue on disk (SQLite, WAL mode)
- Retry with exponential backoff
- Crash recovery (inflight -> pending)
- Restart survival (state persists across process death)
- Delivery on path restoration
- Polite retry (no hammering, blank runs when nothing due)

## What this does NOT prove
- Receiver-side deduplication (phone saw duplicates on earlier test)
- Exactly-once delivery semantics
- Multihop relay

## Next gate
GATE 6 — dedup. Receiver records msg_id and returns same ack
without processing twice.
