# PHARO-LAPSE DIMENSION 4 RECEIPT
## Ecosystem node integration planning artifacts

**Date:** 11 October 2026
**Status:** PENDING_APPLY
**Source:** `spec/ARCHANGEL-INTEGRATION-v0.2.md` (design document; not yet implemented)

## Delivered

- `ecosystem/peer-manifest.json` — a parseable, pending roster of exactly 11
  Constellation nodes. Each record has `peer_id`, `locus`, `role`,
  `public_key: PENDING_KEY`, `via_peer_ids`, and `status`.
- `ecosystem/nodes/root-gate.md`
- `ecosystem/nodes/tesseract-terminus.md`
- `ecosystem/nodes/xinus-clarity.md`
- `ecosystem/nodes/monarch-os.md`
- `ecosystem/nodes/tesseract-a.md`
- `ecosystem/nodes/keira.md`
- `ecosystem/nodes/valkyrie.md`
- `ecosystem/nodes/archangel.md`
- `ecosystem/nodes/project-reclaim.md`
- `ecosystem/nodes/iwa-sage.md`
- `ecosystem/nodes/resonate-earth.md`

Each node note identifies the required repository files, the reference queue
location, the required role-to-outbox boundary, the ten-entry local registry
requirement, and its unresolved dependencies.

## Static validation performed

- Parsed `ecosystem/peer-manifest.json` as JSON.
- Confirmed that the manifest has exactly 11 unique `peer_id` values matching
  the eleven names in the source constellation.
- Confirmed every manifest node has the six required fields and the literal
  placeholder `PENDING_KEY`.
- Confirmed `ecosystem/nodes/` has exactly 11 Markdown files, one named for
  each manifest peer ID, and that every note contains the required integration
  headings.

## LIVE / PENDING / BLOCKED

| Item | State | Evidence / dependency |
|---|---|---|
| Planning manifest and 11 integration notes | LIVE | Files listed above exist locally and are statically validated. |
| Public keys, hosts, ports, and WireGuard overlay identities | PENDING | `PENDING_KEY`; no out-of-band identity or network configuration was available. |
| Per-node queue, listener, role logic, local registry, and route selection | PENDING_APPLY | Requires installation and verification on each node's operator-controlled hardware. |
| Manus project/API changes | PENDING_APPLY | No Manus API or project change was applied or verified. |
| Gate 7 / three-device mesh and live multi-hop delivery | BLOCKED | The source states scaling follows Gate 7; no authorized live overlay or executable gate harness was present here. |
| Commit and push | PENDING | Requires final review and repository authentication outside this task. |

## Boundary

This receipt proves only the existence and static consistency of the planning
artifacts. It does not claim a deployment, listener, queue database, peer
registration, public key, tunnel, message, acknowledgment, telemetry record,
or live test. Empty `via_peer_ids` values are pending placeholders and do not
assert direct connectivity.
