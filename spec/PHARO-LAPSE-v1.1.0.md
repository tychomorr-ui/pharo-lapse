# PHARO-LAPSE PROTOCOL

**Version:** 1.1.0  
**Status:** Specification complete; live gate re-run pending executable test harness and two-device overlay  
**Author:** Tyler Morris, Nexinus RI Systems LLC  
**Date:** 11 October 2026  
**Category:** Informational / Experimental  
**Obsoletes:** PHARO-LAPSE-v1.0.0.md  
**Reference Implementation:** nexinus_queue.py, phone_inbox_dedup.py, NEXINUS-WG-SIGNED-PROBE.py

---

## Abstract

The Pharo-Lapse Protocol is a store-and-forward message delivery protocol for sovereign devices operating over intermittent or unavailable network infrastructure. It provides signed end-to-end delivery with exactly-once semantics, cryptographic provenance, durable queueing on both endpoints, and optional multi-hop forwarding. The protocol operates above any carrier that provides IP connectivity — Wi-Fi, Ethernet, cellular, satellite, or local mesh radio — and does not require the public internet, cloud brokers, certificate authorities, or any third-party service.

Version 1.1.0 preserves the v1.0.0 envelope and queue rules while adding route history, hop limits, peer-registry transit declarations, phase-anchored signing, and deterministic loop prevention. A v1.0.0 peer remains interoperable as a direct, single-hop peer when the v1.1.0 extensions are absent.

This document specifies the wire format, signing domains, forwarding rules, registry extension, phase model, lapse ordering discipline, and security invariants. The four historical gate receipts in `tests/` remain evidence for the v1.0.0 implementation; this repository currently contains no executable test harness capable of re-running those gates under v1.1.0 semantics.

---

## 1. Conventions and Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119.

**Peer** — a device with a canonical identity. Each peer is identified by a stable `peer_id` string and a long-term Ed25519 public key.

**Envelope** — the signed wire-format message described in Section 4.

**Origin envelope** — the sender-created envelope containing the immutable message content and the sender signature.

**Forwarding record** — a signed, append-only record made by a relay when it accepts an envelope for another peer.

**Outbox** — the durable on-disk queue of messages awaiting delivery or acknowledgment.

**Inbox** — the durable on-disk table of messages that have been received and verified at least once.

**Ack** — a signed envelope of type `ack` returned by the final recipient upon successful delivery.

**Lapse** — a logical ordering unit. Two operations in the same lapse are simultaneous; operations in different lapses are ordered. Lapses are monotonic per peer.

**Phase** — the current mesh operating mode: `DAY`, `NIGHT`, or `TWILIGHT`. Phase is derived from observed peer reachability, not from a wall clock.

**CID** — Content Identifier, as used in IPFS. This document uses CIDv1 with dag-json codec and sha2-256 multihash.

**Origin CID** — the CID of the immutable origin content and sender signature. It remains stable while a message is forwarded.

**Pin** — a peer's public key, stored locally by the operator and used to verify inbound signatures. Pins are established out of band.

**Transit peer** — a relay that accepts a valid envelope and forwards it without becoming the message recipient.

---

## 2. Introduction

Existing transport protocols assume reliable paths. TCP requires bidirectional connectivity for the duration of a session. TLS requires a trusted certificate authority. HTTP requires a reachable server. Messaging protocols built on top of these inherit their assumptions: when the path is interrupted, delivery fails.

In environments where infrastructure is intermittent, contested, or absent — wildfire perimeters, disaster response zones, rural benefit delivery, military forward positions, offshore platforms — this assumption is invalid. Messages must be held locally and delivered when the path returns. The protocol must guarantee delivery without assuming continuous connectivity.

The Pharo-Lapse Protocol addresses this by treating the path as a resource that appears and disappears, and by holding messages durably at each endpoint until a delivery opportunity is observed. It does not attempt to maintain connectivity. It maintains delivery.

### 2.1 Design Goals

1. **Delivery guarantee.** A message submitted to the outbox MUST eventually be either delivered (acked) or marked dead by policy. No message is silently dropped.
2. **Exactly-once semantics.** A message with a given `msg_id` MUST be processed at most once at the recipient, regardless of how many times the envelope is transmitted or forwarded.
3. **End-to-end provenance.** The origin signature MUST bind the sender's identity, the recipient's identity, the payload, the message ID, the phase anchor, and the origin route parameters. Relays MUST NOT be able to forge or modify origin content.
4. **Independent forwarding.** A transit peer MAY forward a message without a broker, certificate authority, or central routing service.
5. **Loop freedom.** A conforming peer MUST reject a route that repeats a peer or exceeds `max_hops`.
6. **Determinism.** Given the same canonical state, the same phase, and the same lapse, a peer's delivery decision MUST be reproducible.
7. **Self-healing.** The protocol MUST recover from process death, crash, and restart without loss or duplication.

### 2.2 Non-Goals

The protocol does not provide confidentiality (provided by transport layer), anonymity (identities are canonical and pinned), broadcast or multicast (all messages are pairwise), real-time delivery guarantees (the protocol is store-and-forward), or a consensus mechanism (no distributed agreement is required).

---

## 3. Architecture

The protocol occupies the layer above the transport and below the application. Every peer is symmetric. Any peer MAY initiate delivery to any other peer for which it holds a pin and a reachable address.

A peer's address is an overlay IP and port assigned by the transport layer. The mapping from `peer_id` to overlay address is stored in the local peers table and is established out of band.

A direct delivery has one forwarding hop: sender to recipient. A multi-hop delivery has one or more transit peers. Transit peers store the full envelope durably before attempting the next hop. A transit peer does not decrypt or re-sign the origin content; it verifies the origin signature and adds only its own forwarding record.

---

## 4. Wire Format

### 4.1 Envelope

An envelope is a JSON object with the following fields. Fields marked **v1.1** are extensions. A v1.0 peer that does not understand an extension MUST treat the envelope as a v1.0 direct-delivery envelope only if `route_history` is absent and `max_hops` is absent; otherwise it MUST return an unsupported-extension error without processing the body.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `msg_id` | string (UUID v4) | MUST | Unique identifier for this message |
| `created_at` | string (ISO 8601 UTC) | MUST | Creation timestamp |
| `sender_peer_id` | string | MUST | Canonical origin identity |
| `recipient_peer_id` | string | MUST | Canonical final recipient |
| `body` | string | MUST | Message payload, max 4096 characters |
| `phase` | string | MUST | `DAY`, `NIGHT`, or `TWILIGHT` |
| `lapse` | integer | MUST | Monotonic per sender |
| `phase_anchor` | string | v1.1 MUST; v1.0 default | `PHARO-LAPSE-PHASE/1|<phase>|<lapse>` |
| `prev_cid` | string or null | MUST | CID of the sender's previous envelope, or null for the first |
| `type` | string | MUST | `message`, `ack`, or `ping` |
| `route_history` | array of peer_id strings | v1.1 MUST; v1.0 default | Ordered peers that have accepted the envelope, including the origin sender |
| `max_hops` | integer 1–64 | v1.1 MUST; v1.0 default | Maximum number of transit acceptances after the origin |
| `origin_cid` | string | v1.1 MUST; v1.0 default | Stable CID of the immutable origin content |
| `sig` | string (base64) | MUST | Ed25519 origin signature over the origin signing domain |
| `forwarding` | array | v1.1 MAY | Append-only forwarding records, one per transit acceptance |
| `cid` | string | MUST | CIDv1 over the complete current envelope without the `cid` field |

The v1.0 defaults are: `phase_anchor = PHARO-LAPSE-PHASE/1|<phase>|<lapse>`, `route_history = [sender_peer_id]`, `max_hops = 1`, and `origin_cid = cid` as computed over the v1.0 envelope. A v1.1 implementation MUST NOT silently apply these defaults to a malformed v1.1 envelope that advertises an unsupported version.

### 4.2 Canonical JSON

All object keys are sorted lexicographically by Unicode code point. No insignificant whitespace is emitted. UTF-8 encoding is used. Non-ASCII characters are preserved as UTF-8. Number representation follows ECMAScript `Number.prototype.toString()` rules for the value range used here. Arrays preserve order.

The signature and CID computations MUST use the exact canonical serialization defined below. Implementations MUST reject duplicate JSON object keys before canonicalization.

### 4.3 Signing Domains and CID Domains

The **origin signing domain** is the canonical object containing every field in Section 4.1 except `sig`, `cid`, `forwarding`, and `route_history`. It includes `phase`, `lapse`, `phase_anchor`, `max_hops`, and `origin_cid` when present. The origin signature therefore binds the message, final recipient, phase, lapse, and hop budget, but not mutable transit history.

For v1.1, `origin_cid` is the CIDv1 computed over the origin signing-domain object plus the origin `route_history` and `max_hops`, before any forwarding record is appended. The `origin_cid` MUST remain unchanged at every hop.

The **current envelope CID** is the CIDv1 dag-json sha2-256 digest over the complete current envelope without the `cid` field. A relay MUST recompute `cid` after adding its forwarding record. A recipient MUST verify both `origin_cid` and the current `cid`.

A v1.0 envelope continues to use its complete envelope without `cid` as the signing and CID input, as specified by v1.0.0.

### 4.4 Ack Envelope

An ack is an envelope with `type` set to `ack` and `body` containing `acked_msg_id`, `acked_origin_cid`, `stored_at`, and `route_history`. The ack is signed by the final recipient. The sender MUST verify the ack signature against the pinned recipient key and MUST verify that `acked_msg_id` and `acked_origin_cid` match the outbound message.

### 4.5 Forwarding Record

A forwarding record is an object with:

```json
{
  "peer_id": "relay-a",
  "accepted_at": "2026-10-11T20:00:00Z",
  "lapse": 17,
  "previous_cid": "<current-cid-before-acceptance>",
  "next_peer_id": "relay-b",
  "sig": "<base64-ed25519-signature>"
}
```

The relay's signature covers the record without `sig`, using its pinned local identity. The record MUST be appended atomically with the relay's durable queue insert. The relay MUST NOT alter `body`, `sender_peer_id`, `recipient_peer_id`, `phase`, `phase_anchor`, `lapse`, `prev_cid`, `type`, `max_hops`, or `origin_cid`.

---

## 5. Protocol Rules

Every conforming implementation MUST implement the following rules.

### 5.1 Rule 1 — Identity is Hardware-Bound

Every peer MUST generate its long-term Ed25519 keypair inside a hardware security module (TPM, StrongBox, Secure Enclave, or equivalent) if such a module is available. The private key MUST NOT exist in general-purpose memory or on general-purpose storage. Signing operations MUST be performed by the hardware module.

If no hardware module is available, the keypair MAY be generated in software, and this fact MUST be recorded in the envelope's `hw_bound` field. Peers receiving envelopes with `hw_bound: false` MAY apply stricter policy.

### 5.2 Rule 2 — Every Message is Signed and Content-Addressed

Every envelope MUST carry a valid origin signature and a CID. The recipient MUST verify the origin signature against the sender's pinned key before application processing. The recipient MUST recompute `origin_cid` and the current `cid` and compare both. If verification fails, the envelope MUST be discarded and an error response returned.

### 5.3 Rule 3 — Every Peer Holds Its Own Queue

Every peer MUST maintain a durable outbox and inbox. A transit peer MUST write the accepted envelope and forwarding record before any next-hop delivery attempt. On process start, any outbox entry with state `inflight` MUST be reset to `pending` and retried.

The retry schedule MUST be non-decreasing. The reference implementation uses [30, 60, 120, 240, 480, 600] seconds with +/- 10% jitter, capped at 600 seconds. Implementations MAY use a different schedule but MUST satisfy the non-decreasing property and MUST NOT retry faster than every 10 seconds for a given message.

The maximum attempt count SHOULD be 20. After that, the message MUST be marked dead and no further attempts MAY be made automatically. The default message TTL SHOULD be 72 hours. After TTL expiry, the message MUST be marked expired.

### 5.4 Rule 4 — Dedup is by msg_id

The final recipient MUST maintain a persistent inbox table keyed by `msg_id`. A transit peer MUST maintain a persistent transit table keyed by (`msg_id`, `origin_cid`). On receiving an envelope, a peer MUST perform the appropriate dedup lookup before expensive signature verification. Duplicate final deliveries return the cached ack; duplicate transit deliveries return the cached forwarding result. No duplicate MAY trigger application processing or a second forwarding action.

### 5.5 Rule 5 — Forwarding is Bounded and Loop-Free

A peer MAY act as a transit peer only when the registry permits it and the peer has a reachable next hop. Before accepting a transit envelope, it MUST verify:

1. The origin signature, origin CID, current CID, and every prior forwarding record.
2. The local peer is not already present in `route_history`.
3. `len(route_history) - 1 < max_hops` before adding the local acceptance.
4. The proposed next peer is not present in `route_history` and is not the final recipient's excluded peer.
5. The envelope's `recipient_peer_id` is not the local peer unless this is final delivery.

The relay then appends its own ID to `route_history`, appends one forwarding record, persists the new current CID, and queues the next-hop transmission. A peer MUST reject a repeated route with `LOOP_DETECTED` and a route over the hop budget with `MAX_HOPS_EXCEEDED`. These rejections MUST NOT mutate the application inbox.

---

## 6. Queue State Machine

### 6.1 Outbox States

| State | Meaning |
|-------|---------|
| `pending` | Awaiting delivery attempt. `next_attempt_at` determines when. |
| `inflight` | Currently being transmitted. Reset to pending on restart. |
| `acked` | Delivery confirmed by recipient signature. Terminal. |
| `dead` | Max attempts exceeded or hard failure. Terminal unless operator intervenes. |
| `expired` | TTL exceeded. Terminal. |

A transit queue MUST retain the original `origin_cid`, the current envelope CID, the next peer, and the forwarding record that caused the queue entry. Deleting a transit record before final ack is non-conforming.

### 6.2 Crash Recovery

On process start, the following statements MUST be executed before any other operation:

```sql
UPDATE outbox
SET state = 'pending', last_error = 'recovered from crash'
WHERE state = 'inflight';

UPDATE outbox
SET state = 'expired'
WHERE state = 'pending' AND expires_at < now();
```

Transit stores MUST apply equivalent recovery to forwarding records whose next-hop attempt was interrupted. These statements ensure that any message in transit at failure is retried and that any message past its TTL is not retried.

---

## 7. Phase Model

### 7.1 Phase Definition

Phase is derived from the observed reachability of pinned peers. It is not a wall-clock property. It reflects the current operational state of the mesh as seen from this peer.

Let P be the set of pinned peers, and R be the subset currently responding to keepalives within the last 60 seconds.

| Phase | Condition | Retry schedule | Probe interval |
|-------|-----------|----------------|----------------|
| `DAY` | R / P >= 0.5 | Short | 25 seconds |
| `NIGHT` | R / P < 0.25 | Long (5x base) | 300 seconds |
| `TWILIGHT` | otherwise | Intermediate | 120 seconds |

### 7.2 Phase Transitions

Transitions between phases MUST be hysteretic. A single missing peer response MUST NOT trigger a `DAY` to `NIGHT` transition. The reference implementation requires three consecutive lapses below the threshold before transitioning to `NIGHT`, and a single successful response from any pinned peer to transition from `NIGHT` to `DAY`.

### 7.3 Phase-Anchored Signing

Every origin envelope MUST include `phase_anchor` equal to the exact ASCII string `PHARO-LAPSE-PHASE/1|<phase>|<lapse>`, where `<phase>` and `<lapse>` are the values in the same envelope. The origin signature MUST cover `phase`, `lapse`, and `phase_anchor` together. A verifier MUST reject an envelope if the string does not recompute exactly.

A forwarding record MUST include the relay's phase anchor using the forwarding record's `lapse` and the relay's observed phase. The relay signature MUST cover that anchor. A receipt produced in `DAY` MUST NOT verify as a receipt from `NIGHT` even if all other fields are identical.

A peer MUST NOT rewrite an origin phase or lapse while forwarding. If local conditions change, the relay records its current phase only in its forwarding record and applies its own current phase to the next-hop scheduling decision.

---

## 8. Lapse and Route Discipline

### 8.1 Lapse Definition

A lapse is a monotonic integer that increments on each successful delivery attempt, each received envelope, and each phase transition. The lapse is local to a peer; two peers MAY be at different lapse values at the same wall-clock moment. This is intentional: the lapse is a logical clock, not a physical clock.

### 8.2 Ordering

Envelopes from the same sender MUST have strictly increasing lapse values. An envelope with a lapse less than or equal to the highest lapse previously seen from that sender MUST be rejected as a stale replay, unless it is a duplicate with the same `msg_id` as a previously accepted envelope, in which case Section 5.4 applies.

### 8.3 Receipt Lapse

The lapse value at the moment of signing MUST be included in the receipt. Replay of a receipt at a different lapse is invalid.

### 8.4 Route History and Loop Prevention

`route_history[0]` MUST equal `sender_peer_id`. Each accepted transit hop appends exactly one peer ID. The final recipient MAY append itself when storing the message; if it does, it MUST do so before computing the ack's route binding. A peer ID MUST appear at most once in `route_history`.

`max_hops` counts transit acceptances after the origin and before final delivery. `max_hops = 1` therefore permits direct delivery through the origin-to-recipient path and does not permit a transit relay. A sender that wants one relay MUST set `max_hops >= 2`.

A route is invalid if `len(route_history) - 1 > max_hops`, if the local peer already appears in the route, or if the next peer appears in the route. The invalid route MUST be rejected without forwarding.

---

## 9. Peer Registry Extension

The v1.0 peer record is extended as follows:

```json
{
  "peer_id": "relay-a",
  "host": "10.9.0.3",
  "port": 7777,
  "public_key_b64": "<base64>",
  "via_peer_ids": ["penguin", "phone"],
  "last_seen": "2026-10-11T20:00:00Z"
}
```

`via_peer_ids` is an ordered list of peers through which this address is reachable. It is a routing hint, not authorization. A peer MUST NOT select a route containing a repeated ID. An empty or absent `via_peer_ids` means direct reachability is expected. Registry entries MUST be locally pinned or authenticated out of band; registry data alone does not establish identity.

When multiple routes are available, selection MUST be deterministic: filter routes that violate Section 8.4, then choose the route with the fewest remaining hops; break ties by lexicographic order of the complete peer-ID path. Implementations MAY use reachability and phase metrics to remove unavailable routes before this deterministic tie-break.

---

## 10. Delivery Algorithm

### 10.1 Sender Loop

```text
loop:
  now = current_time()
  candidates = SELECT from outbox
               WHERE state = 'pending'
                 AND (next_attempt_at IS NULL OR next_attempt_at <= now)
               ORDER BY created_at LIMIT 10
  if candidates is empty: if one_shot return; sleep; continue
  for each msg in candidates:
      mark_inflight
      result = attempt_delivery_or_forward
      handle_result
```

### 10.2 Delivery Attempt

Look up the peer and its `via_peer_ids`. Select a deterministic valid route. POST the current envelope to `http://peer.host:peer.port/inbox` with a timeout of 30 seconds. Catch timeout, connection refused, and other transport errors as `RETRYABLE_ERROR`. On a 200 response, parse the ack, verify the recipient signature, verify `acked_msg_id`, verify `acked_origin_cid`, and verify the route binding. On any failure, return the appropriate error class.

### 10.3 Transit Attempt

A transit peer verifies the origin and all forwarding records, performs the loop and hop checks, writes the transit record durably, appends its forwarding record, recomputes the current CID, and queues the next hop. It MUST return a signed forwarding receipt only after the durable write succeeds. If no valid next hop exists, it returns `NO_ROUTE` and retains the message in `pending` until policy marks it dead or expired.

### 10.4 Result Handling

`SUCCESS(ack)`: mark acked, store ack. `RETRYABLE_ERROR`: increment attempts, compute next delay, mark pending. `HARD_ERROR`: mark dead, record reason. `LOOP_DETECTED`, `MAX_HOPS_EXCEEDED`, `INVALID_ORIGIN`, and `INVALID_FORWARDING_RECORD` are hard errors. If attempts reach 20, mark dead regardless.

### 10.5 Recipient Listener

On POST `/inbox`: parse JSON. Perform the applicable dedup lookup first. Otherwise verify the origin signature, all forwarding signatures, recompute and compare CIDs, check recipient match, check phase anchor, check lapse monotonicity, check route history, check hop budget, check type validity, and check body length. On all pass, begin a transaction: insert into inbox, update peer last_lapse, and persist the cached ack. Commit. Return 200 with canonical ack JSON.

The dedup check MUST occur before any expensive verification step. This is a deliberate design choice: the common case for a retry is a duplicate, and the dedup check resolves duplicates in a single indexed lookup.

---

## 11. Receipt Format

Every successful final delivery produces a signed receipt at the recipient. The receipt is an ack envelope. Optionally, the sender and every transit peer MAY produce a receipt for the outbound or forwarding side.

An outbound receipt is a JSON object with `receipt_id` (UUID v4), `msg_id`, `sender_peer_id`, `recipient_peer_id`, `input_hash` (sha256 of canonical origin envelope), `origin_cid`, `state_hash` (sha256 of outbox state), `rule_set_version` (`PHARO-LAPSE-1.1.0`), `authority_state` (`NOT_CONFIGURED` or `OPERATOR_APPROVED`), `model_inference` (always false), `external_ai` (always false), `phase`, `lapse`, `route_history`, `max_hops`, `result_state` (`acked`, `queued`, `dead`, `expired`), and `sig` (Ed25519 signature over canonical JSON).

Receipts MUST be reproducible. Given the same input envelope, the same outbox state, the same phase, the same lapse, and the same route history, the receipt MUST be byte-identical.

---

## 12. Security Considerations

### 12.1 Threat Model

The protocol assumes passive eavesdropping on the transport (confidentiality provided by transport layer), active man-in-the-middle (integrity provided by envelope and forwarding signatures plus CID verification), replay (rejected by dedup, lapse monotonicity, and route history), impersonation (rejected by pin verification), and process crash at any point (recovered by crash recovery).

The protocol does not assume compromise of an endpoint, denial of service at the transport, or user error.

### 12.2 Attack Class Elimination

The following attack classes are addressed by construction: prompt injection (no prompt channel), SQL injection (parameterized queries), command injection (no shell invocation), replay (dedup and lapse), impersonation (pin verification), man-in-the-middle (signatures and CIDs), tampering (origin and current CID verification), forwarding loops (route history and hop budget), and central compromise (no central authority).

### 12.3 Residual Risk

Physical seizure, endpoint compromise, key theft where hardware binding is unavailable, revocation lag, side-channel leakage, route exhaustion, and denial of service remain residual risks. Implementations SHOULD use hardware-backed keys, signed pin updates, per-peer rate limits, queue size caps, and operator-visible route rejection logs.

---

## 13. Test Requirements

A v1.1.0 implementation MUST provide executable tests for:

1. Direct v1.0-compatible delivery with absent extensions.
2. Phase-anchor mismatch rejection.
3. Origin signature rejection after body, phase, lapse, or hop-budget mutation.
4. One-relay forwarding with stable `origin_cid` and changed current `cid`.
5. Forwarding-signature verification.
6. Repeated-peer loop rejection.
7. Hop-budget rejection.
8. Transit crash recovery without duplicate forwarding.
9. Final-recipient dedup with cached ack.
10. Deterministic route selection.
11. Route registry `via_peer_ids` parsing.
12. Backward-compatible direct delivery under the four historical gates.

The v1.0.0 historical receipts in `tests/` are not executable tests and MUST NOT be presented as a fresh v1.1.0 run. A live v1.1.0 gate receipt MUST include the commit hash, test command, environment, message IDs, CIDs, route history, and UTC timestamps.

---

## 14. Historical Gate Mapping

### 14.1 Gate 3 — Transport Without Internet

The v1.1.0 transport requirement is unchanged. A valid receipt MUST show a real HTTP exchange over the WireGuard overlay with public internet unavailable.

### 14.2 Gate 4 — Signed Envelope and Signed Ack

The direct path remains compatible. The sender and recipient MUST additionally verify `phase_anchor` when the v1.1.0 extensions are present.

### 14.3 Gate 5 — Store-and-Forward with Crash Recovery

The sender and any transit peer MUST recover `inflight` entries to `pending`. A transit crash MUST NOT produce two forwarding records or two next-hop application actions.

### 14.4 Gate 6 — Exactly-Once Delivery

The final recipient continues to deduplicate by `msg_id`. Transit peers deduplicate by (`msg_id`, `origin_cid`) and MUST return a cached forwarding result without forwarding twice.

The repository's historical receipts document the v1.0.0 runs; a new executable harness is required before these four gates can be marked re-verified under v1.1.0 semantics.

---

## 15. Implementation Notes

The reference implementation uses SQLite with WAL journaling. The outbox and inbox are single tables with primary keys on `msg_id`. A v1.1.0 implementation adds transit records, forwarding records, `origin_cid`, `current_cid`, `max_hops`, `route_history`, and `via_peer_ids`. Indexes on state, next attempt time, peer ID, and origin CID support the delivery loop.

The transport is HTTP/1.0 over WireGuard. HTTP/1.1 or HTTP/2 MAY be used. The endpoint is a single POST to `/inbox`. No other endpoints are required.

The delivery loop MAY run as a single thread. SQLite WAL supports one writer and multiple readers. Concurrent delivery to multiple peers is possible but not required.

Any implementation that produces envelopes conforming to Section 4 and follows the rules of Section 5 will interoperate. The specific storage engine, HTTP version, and programming language are not constrained.

---

## 16. Acknowledgments

The protocol takes its name from two sources. Pharo refers to the pheromone trails left by ants, which persist after the individual that laid them has departed and are used by subsequent individuals to find their way. Lapse refers to the interval between two valid states — a rhythm rather than a gap.

The underlying metaphor is the Monarch butterfly's multi-generational migration. No individual butterfly completes the round trip; the pattern is carried across generations. The pattern is the intelligence. The individuals are the instruments. The receipts are the record.

The protocol was designed and implemented by Tyler Morris at Nexinus RI Systems LLC.

---

## 17. References

[RFC 2119] Bradner, S., “Key words for use in RFCs to Indicate Requirement Levels”, BCP 14, RFC 2119, March 1997.

[RFC 8032] Josefsson, S., Liusvaara, I., “Edwards-Curve Digital Signature Algorithm (EdDSA)”, RFC 8032, January 2017.

[RFC 7748] Langley, A., Hamburg, M., Turner, S., “Elliptic Curves for Security”, RFC 7748, January 2016.

[CID] Benet, J., “Content Addressable aRchives”, IPFS, 2014–2026.

[OTS] Todd, P., “OpenTimestamps: Scalable, Trustless, Distributed Timestamping with Bitcoin”, 2016–2026.

[WG] Donenfeld, J., “WireGuard: Next Generation Kernel Network Tunnel”, NDSS 2017.

---

**End of Specification**
