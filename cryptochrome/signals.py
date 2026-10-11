"""Inbox arrival-history sensor for Cryptochrometer."""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def read_arrival_history(
    inbox_path: str | Path | None = None,
    *,
    rows: Iterable[tuple[str, str]] | None = None,
) -> dict[str, list[str]]:
    """Return peer -> ordered arrival timestamps.

    `rows` is an injectable deterministic source. `inbox_path` accepts JSONL records
    with `peer_id` and either `received_at` or `stored_at`, or a SQLite inbox table.
    """
    result: dict[str, list[str]] = defaultdict(list)
    if rows is not None:
        for peer_id, timestamp in rows:
            result[str(peer_id)].append(str(timestamp))
        return dict(result)
    if inbox_path is None:
        return {}
    path = Path(inbox_path)
    if not path.exists():
        return {}
    if path.suffix in {".db", ".sqlite", ".sqlite3"}:
        with sqlite3.connect(path) as conn:
            for peer_id, timestamp in conn.execute(
                "SELECT peer_id, received_at FROM inbox ORDER BY received_at"
            ):
                result[str(peer_id)].append(str(timestamp))
        return dict(result)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        peer_id = record.get("peer_id") or record.get("sender_peer_id")
        timestamp = record.get("received_at") or record.get("stored_at")
        if peer_id is not None and timestamp is not None:
            result[str(peer_id)].append(str(timestamp))
    return dict(result)


def sensor_snapshot(history: dict[str, list[str]]) -> dict[str, dict[str, object]]:
    """Summarize arrival history without inventing reachability."""
    return {
        peer_id: {"arrivals": len(timestamps), "last_arrival": timestamps[-1] if timestamps else None}
        for peer_id, timestamps in sorted(history.items())
    }
