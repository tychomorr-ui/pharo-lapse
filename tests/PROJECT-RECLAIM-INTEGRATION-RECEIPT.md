# Project Reclaim Pharo-Lapse Integration Receipt

**Date:** 2026-10-16
**Status:** READY for sanitized v1 reference events; live signed delivery PENDING

## Added artifacts

- `applications/project-reclaim/adapter-template.py`
- `applications/project-reclaim/add-to-pharo-lapse.sh`
- `applications/project-reclaim/INTEGRATION-FLOW.md`
- `applications/project-reclaim/test_adapter_boundary.py`

## v1 reference event

```json
{
  "event_id": "PR-TEST-001",
  "event_type": "status",
  "created_at": "2026-10-16T16:00:00Z",
  "priority": "routine",
  "origin": "project-reclaim",
  "message": "Project Reclaim reference status test"
}
```

## Validation command

```bash
python3 applications/project-reclaim/test_adapter_boundary.py
```

Expected and observed result:

```text
Project Reclaim adapter: READY for sanitized v1 reference events
Project Reclaim invalid-event rejection: PASS
No network delivery was attempted
```

## Boundary

The adapter now validates and deterministically serializes the sanitized v1
reference event. The bridge can place that body in the legacy local SQLite
reference queue, but that queue is unsigned and does not verify signed acks.
A live signed WireGuard delivery remains unclaimed until a real recipient key,
recipient listener, and signed receipt are configured and tested.
