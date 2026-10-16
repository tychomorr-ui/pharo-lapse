# Project Reclaim Pharo-Lapse Integration Receipt

**Date:** 2026-10-16
**Status:** PENDING / BLOCKED at application boundary

## Added artifacts

- `applications/project-reclaim/adapter-template.py`
- `applications/project-reclaim/INTEGRATION-FLOW.md`
- `applications/project-reclaim/test_adapter_boundary.py`

## Validation

Command:

```bash
python3 applications/project-reclaim/test_adapter_boundary.py
```

Expected and observed result:

```text
Project Reclaim adapter boundary: BLOCKED as designed
No event was fabricated or queued
```

## Boundary

The adapter does not invent a Project Reclaim event schema or create a fake
message. It stops until an authoritative schema, deterministic serializer,
operator approval mechanism, recipient peer configuration, and live signed
acknowledgment procedure are supplied.

The existing `project-reclaim` manifest entry remains `PENDING_APPLY`; no live
WireGuard handshake or application delivery is claimed by this receipt.
