# PHARO-LAPSE PROTOCOL

**Version:** 1.0.0
**Status:** Reference Implementation Complete — Verified Across Four Test Classes
**Author:** Tyler Morris, Nexinus RI Systems LLC
**Date:** 9 October 2026
**Category:** Informational / Experimental
**Reference Implementation:** nexinus_queue.py, phone_inbox_dedup.py, NEXINUS-WG-SIGNED-PROBE.py

---

## Abstract

The Pharo-Lapse Protocol is a store-and-forward message delivery protocol for sovereign devices operating over intermittent or unavailable network infrastructure. It provides signed end-to-end delivery with exactly-once semantics, cryptographic provenance, and durable queueing on both endpoints. The protocol operates above any carrier that provides IP connectivity — Wi-Fi, Ethernet, cellular, satellite, or local mesh radio — and does not require the public internet, cloud brokers, certificate authorities, or any third-party service. This document specifies the wire format, the four protocol rules, the queue state machine, the phase model, the lapse ordering discipline, and the security invariants. A reference implementation has been verified across four test classes: transport without internet, signed envelope exchange, durable queue recovery, and duplicate suppression. All four tests pass.

---

## 1. Conventions and Terminology

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in this document are to be interpreted as described in RFC 2119.

**Peer** — a device with a canonical identity. Each peer is identified by a stable peer_id string and a long-term Ed25519 public key.

**Envelope** — the signed wire-format message described in Section 4.

**Outbox** — the durable on-disk queue of messages awaiting delivery or acknowledgment.

**Inbox** — the durable on-disk table of messages that have been received and verified at least once.

**Ack** — a signed envelope of type ack returned by the recipient upon successful delivery.

**Lapse** — a logical ordering unit. Two operations in the same lapse are simultaneous; operations in different lapses are ordered. Lapses are monotonic per peer.

**Phase** — the current mesh operating mode: DAY, NIGHT, or TWILIGHT. Phase is derived from observed peer reachability, not from a wall clock.

**CID** — Content Identifier, as used in IPFS. This document uses CIDv1 with dag-json codec and sha2-256 multihash.

**Pin** — a peer's public key, stored locally by the operator and used to verify inbound signatures. Pins are established out of band.

---

## 2. Introduction

Existing transport protocols assume reliable paths. TCP requires bidirectional connectivity for the duration of a session. TLS requires a trusted certificate authority. HTTP requires a reachable server. Messaging protocols built on top of these inherit their assumptions: when the path is interrupted, delivery fails.

In environments where infrastructure is intermittent, contested, or absent — wildfire perimeters, disaster response zones, rural benefit delivery, military forward positions, offshore platforms — this assumption is invalid. Messages must be held locally and delivered when the path returns. The protocol must guarantee delivery without assuming continuous connectivity.

The Pharo-Lapse Protocol addresses this by treating the path as a resource that appears and disappears, and by holding messages durably at each endpoint until a delivery opportunity is observed. It does not attempt to maintain connectivity. It maintains delivery.

### 2.1 Design Goals

1. **Delivery guarantee.** A message submitted to the outbox MUST eventually be either delivered (acked) or marked dead by policy. No message is silently dropped.

2. **Exactly-once semantics.** A message with a given msg_id MUST be processed at most once at the recipient, regardless of how many times the envelope is transmitted.

3. **End-to-end provenance.** The signature on the envelope MUST bind the sender's identity, the recipient's identity, the payload, and the message ID. Relays MUST NOT be able to forge, modify, or replay messages.

4. **Independence.** The protocol MUST function without the public internet, without a central broker, and without a trusted third party.

5. **Determinism.** Given the same canonical state, the same phase, and the same lapse, a peer's delivery decision MUST be reproducible.

6. **Self-healing.** The protocol MUST recover from process death, crash, and restart without loss or duplication.

### 2.2 Non-Goals

The protocol does not provide confidentiality (provided by transport layer), anonymity (identities are canonical and pinned), broadcast or multicast (all messages are pairwise), real-time delivery guarantees (the protocol is store-and-forward), or a consensus mechanism (no distributed agreement is required).

---

## 3. Architecture

The protocol occupies the layer above the transport and below the application. Every peer is symmetric. There is no client/server distinction. Any peer MAY initiate delivery to any other peer for which it holds a pin and a reachable address.

A peer's address is an overlay IP and port assigned by the transport layer. The mapping from peer_id to overlay address is stored in the local peers table and is established out of band.

---

## 4. Wire Format

### 4.1 Envelope

An envelope is a JSON object with the following fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| msg_id | string (UUID v4) | MUST | Unique identifier for this message |
| created_at | string (ISO 8601 UTC) | MUST | Creation timestamp |
| sender_peer_id | string | MUST | Canonical identity of the sender |
| recipient_peer_id | string | MUST | Canonical identity of the recipient |
| body | string | MUST | Message payload, max 4096 characters |
| phase | string | MUST | DAY, NIGHT, or TWILIGHT |
| lapse | integer | MUST | Monotonic per sender |
| prev_cid | string or null | MUST | CID of the sender's previous envelope, or null for the first |
| type | string | MUST | message, ack, or ping |
| sig | string (base64) | MUST | Ed25519 signature over canonical JSON |
| cid | string | MUST | CIDv1 dag-json sha2-256 over the envelope without the cid field |

### 4.2 Canonical JSON

The signature and CID cover a canonical serialization of the envelope. All object keys sorted lexicographically by Unicode code point. No insignificant whitespace. UTF-8 encoding. Non-ASCII characters preserved as UTF-8. Number representation follows ECMAScript Number.prototype.toString() rules for the value range used here.

The signature is computed over the UTF-8 bytes of this canonical form. The CID is computed over the same bytes.

### 4.3 Ack Envelope

An ack is an envelope with type set to ack and body containing a JSON object with acked_msg_id, acked_cid, and stored_at fields. The ack is signed by the recipient. Its own cid is computed the same way.

---

## 5. Protocol Rules

Every conforming implementation MUST implement the following four rules.

### 5.1 Rule 1 — Identity is Hardware-Bound

Every peer MUST generate its long-term Ed25519 keypair inside a hardware security module (TPM, StrongBox, Secure Enclave, or equivalent) if such a module is available. The private key MUST NOT exist in general-purpose memory or on general-purpose storage. Signing operations MUST be performed by the hardware module.

If no hardware module is available, the keypair MAY be generated in software, and this fact MUST be recorded in the envelope's hw_bound field. Peers receiving envelopes with hw_bound: false MAY apply stricter policy.

### 5.2 Rule 2 — Every Message is Signed and Content-Addressed

Every envelope MUST be signed by the sender's long-term key. The recipient MUST verify the signature against the sender's pinned key before any other processing. If verification fails, the envelope MUST be discarded and an error response returned.

The envelope MUST carry a CID computed over the canonical bytes. The recipient MUST recompute the CID and compare. If the CIDs do not match, the envelope MUST be discarded.

### 5.3 Rule 3 — Every Peer Holds Its Own Queue

Every peer MUST maintain a durable outbox and inbox. The outbox MUST be written before any delivery attempt is made. On process start, any outbox entry with state inflight MUST be reset to pending and retried.

The retry schedule MUST be non-decreasing. The reference implementation uses [30, 60, 120, 240, 480, 600] seconds with +/- 10% jitter, capped at 600 seconds. Implementations MAY use a different schedule but MUST satisfy the non-decreasing property and MUST NOT retry faster than every 10 seconds for a given message.

The maximum attempt count SHOULD be 20. After that, the message MUST be marked dead and no further attempts MAY be made automatically.

The default message TTL SHOULD be 72 hours. After TTL expiry, the message MUST be marked expired.

### 5.4 Rule 4 — Dedup is by msg_id

The recipient MUST maintain a persistent inbox table keyed by msg_id. On receiving an envelope: if msg_id exists in the inbox, return the cached ack and MUST NOT reprocess. If msg_id does not exist, perform full verification and, on success, store the message and return a fresh signed ack.

Duplicate envelopes MUST NOT increment any counter, trigger any application-level action, or modify any state except the response cache lookup.

---

## 6. Queue State Machine

### 6.1 Outbox States

| State | Meaning |
|-------|---------|
| pending | Awaiting delivery attempt. next_attempt_at determines when. |
| inflight | Currently being transmitted. Reset to pending on restart. |
| acked | Delivery confirmed by recipient signature. Terminal. |
| dead | Max attempts exceeded. Terminal unless operator intervenes. |
| expired | TTL exceeded. Terminal. |

### 6.2 Crash Recovery

On process start, the following statements MUST be executed before any other operation:

UPDATE outbox SET state = 'pending', last_error = 'recovered from crash' WHERE state = 'inflight';

UPDATE outbox SET state = 'expired' WHERE state = 'pending' AND expires_at < now();

These two statements ensure that any message that was in transit at the moment of failure is retried, and that any message past its TTL is not retried.

---

## 7. Phase Model

### 7.1 Phase Definition

Phase is derived from the observed reachability of pinned peers. It is not a wall-clock property. It reflects the current operational state of the mesh as seen from this peer.

Let P be the set of pinned peers, and R be the subset currently responding to keepalives within the last 60 seconds.

| Phase | Condition | Retry schedule | Probe interval |
|-------|-----------|----------------|----------------|
| DAY | R / P >= 0.5 | Short | 25 seconds |
| NIGHT | R / P < 0.25 | Long (5x base) | 300 seconds |
| TWILIGHT | otherwise | Intermediate | 120 seconds |

### 7.2 Phase Transitions

Transitions between phases MUST be hysteretic. A single missing peer response MUST NOT trigger a DAY to NIGHT transition. The reference implementation requires three consecutive lapses below the threshold before transitioning to NIGHT, and a single successful response from any pinned peer to transition from NIGHT to DAY.

### 7.3 Phase in Receipts

The current phase MUST be included in every envelope. The signature MUST cover the phase field. A receipt produced in DAY MUST NOT verify as a receipt from NIGHT even if all other fields are identical.

---

## 8. Lapse Discipline

### 8.1 Definition

A lapse is a monotonic integer that increments on each successful delivery attempt, each received envelope, and each phase transition. The lapse is local to a peer; two peers MAY be at different lapse values at the same wall-clock moment. This is intentional: the lapse is a logical clock, not a physical one.

### 8.2 Ordering

Envelopes from the same sender MUST have strictly increasing lapse values. An envelope with a lapse less than or equal to the highest lapse previously seen from that sender MUST be rejected as a stale replay, unless it is a duplicate with the same msg_id as a previously accepted envelope, in which case Section 5.4 applies.

### 8.3 Receipt Lapse

The lapse value at the moment of signing MUST be included in the receipt. Replay of a receipt at a different lapse is invalid.

---

## 9. Delivery Algorithm

### 9.1 Sender Loop

loop:
  now = current_time()
  candidates = SELECT from outbox WHERE state = 'pending' AND (next_attempt_at IS NULL OR next_attempt_at <= now) ORDER BY created_at LIMIT 10
  if candidates is empty: if one_shot return; sleep; continue
  for each msg in candidates: mark_inflight; result = attempt_delivery; handle_result

### 9.2 Delivery Attempt

Look up peer. POST to http://peer.host:peer.port/inbox with body = envelope_json, timeout = 30s. Catch timeout, connection refused, and other errors as RETRYABLE_ERROR. On 200 response, parse ack, verify signature, verify msg_id match. On match, return SUCCESS(ack). On any failure, return the appropriate error class.

### 9.3 Result Handling

SUCCESS(ack): mark acked, store ack. RETRYABLE_ERROR: increment attempts, compute next delay, mark pending. HARD_ERROR: mark dead, record reason. If attempts reach 20, mark dead regardless.

### 9.4 Recipient Listener

On POST /inbox: parse JSON. Dedup check first — cheaper than verification. If msg_id exists in inbox, return cached ack. Otherwise verify signature against pin, recompute CID and compare, check recipient match, check phase validity, check lapse monotonicity, check type validity, check body length. On all pass, begin transaction: insert into inbox, update peer last_lapse. Commit. Return 200 with canonical ack JSON.

The dedup check MUST occur before any expensive verification step. This is a deliberate design choice: the common case for a retry is a duplicate, and the dedup check resolves duplicates in a single indexed lookup.

---

## 10. Receipt Format

Every successful delivery produces a signed receipt at the recipient. The receipt is an ack envelope. Optionally, the sender MAY also produce a receipt for the outbound side.

An outbound receipt is a JSON object with receipt_id (UUID v4), msg_id, sender_peer_id, recipient_peer_id, input_hash (sha256 of canonical envelope), state_hash (sha256 of outbox state), rule_set_version (PHARO-LAPSE-1.0.0), authority_state (NOT_CONFIGURED or OPERATOR_APPROVED), model_inference (always false), external_ai (always false), phase, lapse, result_state (acked, queued, dead, expired), and sig (Ed25519 signature over canonical JSON).

Receipts MUST be reproducible. Given the same input envelope, the same outbox state, the same phase, and the same lapse, the receipt MUST be byte-identical.

---

## 11. Security Considerations

### 11.1 Threat Model

The protocol assumes passive eavesdropping on the transport (confidentiality provided by transport layer), active man-in-the-middle (integrity provided by envelope signature and CID), replay (rejected by dedup and lapse monotonicity), impersonation (rejected by pin verification), and process crash at any point (recovered by crash recovery).

The protocol does not assume compromise of the endpoint, denial of service at the transport, or user error.

### 11.2 Attack Class Elimination

The following attack classes are eliminated by construction: prompt injection (no prompt channel), SQL injection (parameterized queries), command injection (no shell invocation), replay (dedup and lapse), impersonation (pin verification), man-in-the-middle (signature and CID), tampering (CID verification), key theft (hardware binding), device cloning (unique hardware module), central compromise (no central authority), race conditions (lapse ordering).

### 11.3 Residual Risk

Physical seizure (mitigated by hardware module), user-level compromise (mitigated by short-lived session keys and user presence), revocation lag (mitigated by revocation lists propagated through signed envelopes), side-channel (mitigated by constant-time code and physical shielding), and DoS (mitigated by per-peer rate limits and queue size caps).

---

## 12. Test Cases

The reference implementation was verified against the following test cases on 9 October 2026.

### 12.1 Gate 3 — Transport Without Internet

An HTTP GET request from one peer to another over a WireGuard overlay, with the public internet unavailable on the carrier network and mobile data disabled at the recipient. Verified.

### 12.2 Gate 4 — Signed Envelope and Signed Ack

A signed envelope transmitted over the same overlay, verified by the recipient against a pinned public key, and acknowledged with a signed receipt that the sender also verified. Message ID and body hash bound to the exchange. Verified.

### 12.3 Gate 5 — Store-and-Forward with Crash Recovery

Three messages queued while the recipient was offline. All three attempts timed out. The sender process was terminated and restarted. Queue state persisted. When the recipient returned, all three messages were delivered and marked acked. Verified.

### 12.4 Gate 6 — Exactly-Once Delivery

Two messages delivered once. Both marked NEW by the recipient, with unique msg_id and sha256 values. Both were then re-queued and re-delivered. Both returned the cached ack, marked DUP, with the same sha256 and no reprocessing. Verified.

### 12.5 Negative-Case Tests

The reference implementation also passes seven negative test cases: malformed public-key encoding, unpinned public key, tampered signed payload, invalid Ed25519 signature, wrong recipient, unsupported protocol, and payload type violation. All seven are rejected with specific error codes.

---

## 13. Implementation Notes

The reference implementation uses SQLite with WAL journaling. The outbox and inbox are single tables with primary keys on msg_id. Indexes on state, next_attempt_at, and peer_id support the delivery loop.

The transport is HTTP/1.0 over WireGuard. HTTP/1.1 or HTTP/2 MAY be used. The endpoint is a single POST to /inbox. No other endpoints are required.

The delivery loop MAY run as a single thread. SQLite WAL supports one writer and multiple readers. Concurrent delivery to multiple peers is possible but not required.

Any implementation that produces envelopes conforming to Section 4 and follows the four rules of Section 5 will interoperate. The specific storage engine, HTTP version, and programming language are not constrained.

---

## 14. Acknowledgments

The protocol takes its name from two sources. Pharo refers to the pheromone trails left by ants, which persist after the individual that laid them has departed and are used by subsequent individuals to find their way. Lapse refers to the interval between two valid states — a rhythm rather than a gap.

The underlying metaphor is the Monarch butterfly's multi-generational migration. No individual butterfly completes the round trip; the pattern is carried across generations. The pattern is the intelligence. The individuals are the instruments. The receipts are the record.

The protocol was designed and implemented by Tyler Morris at Nexinus RI Systems LLC. The reference implementation was validated against the four gates described in Section 12 in a single working session on 9 October 2026.

---

## 15. References

[RFC 2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.

[RFC 8032] Josefsson, S., Liusvaara, I., "Edwards-Curve Digital Signature Algorithm (EdDSA)", RFC 8032, January 2017.

[RFC 7748] Langley, A., Hamburg, M., Turner, S., "Elliptic Curves for Security", RFC 7748, January 2016.

[Cid] Benet, J., "Content Addressable aRchives", IPFS, 2014-2026.

[OTS] Todd, P., "OpenTimestamps: Scalable, Trustless, Distributed Timestamping with Bitcoin", 2016-2026.

[WG] Donenfeld, J., "WireGuard: Next Generation Kernel Network Tunnel", NDSS 2017.

---

**End of Specification**
