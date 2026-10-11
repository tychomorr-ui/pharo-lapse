# PHARO-LAPSE DIMENSION 1 RECEIPT
## Protocol maturity v1.1.0

**Date:** 11 October 2026  
**Status:** PARTIAL  
**Rule set:** `PHARO-LAPSE-1.1.0`  
**Repository commit at start:** `a105c2f`  
**Live gate result:** BLOCKED — no executable gate-test harness or three-device overlay is present in this sandbox

## Delivered

- `spec/PHARO-LAPSE-v1.1.0.md`
- Backward-compatible v1.0.0 direct-delivery defaults
- Phase-anchored signing domain
- `route_history`, `max_hops`, and stable `origin_cid`
- Append-only signed forwarding records
- Multi-hop forwarding and deterministic loop prevention
- Peer registry `via_peer_ids` extension
- Transit queue durability and crash-recovery requirements
- v1.1.0 test requirements and honest mapping of the four historical gates

## Static verification performed

The specification was inspected for the required v1.1.0 elements:

- Version is `1.1.0`.
- `phase_anchor` is defined and included in the origin signing domain.
- `route_history` and `max_hops` are defined with defaults for v1.0 compatibility.
- `origin_cid` is stable across forwarding and current `cid` is recomputed per envelope state.
- `via_peer_ids` is defined in the peer registry extension.
- Loop prevention and TTL/hop enforcement are normative.
- The four historical receipts are explicitly not relabeled as fresh v1.1.0 results.

## LIVE / PENDING / BLOCKED

| Item | State | Evidence |
|---|---|---|
| v1.1.0 specification | LIVE | `spec/PHARO-LAPSE-v1.1.0.md` exists in the working tree |
| v1.0.0 backward-compatible defaults | LIVE | Sections 4.1–4.3 of the specification |
| Four gates re-run under v1.1.0 semantics | BLOCKED | `tests/` contains receipts only; no executable gate tests |
| Three-device/multi-hop live proof | BLOCKED | OCI `VM.Standard.A1.Flex` capacity unavailable in San Jose; no alternate hub active |
| Commit and push | PENDING | Requires final review of the generated specification and receipt |

## Boundary

No claim is made that v1.1.0 has passed the four gates. The existing Gate 3–6 files are historical v1.0.0 evidence and remain unchanged.

**Credits consumed:** Not available from the local execution environment; no credit figure is claimed.
