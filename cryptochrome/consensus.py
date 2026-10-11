"""Durable outbox-depth sensor for Cryptochrometer."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


def outbox_depths(
    db_path: str | Path | None = None,
    *,
    rows: Iterable[tuple[str, int]] | None = None,
) -> dict[str, int]:
    """Return destination -> non-terminal queue depth."""
    if rows is not None:
        return {str(peer_id): int(depth) for peer_id, depth in sorted(rows)}
    if db_path is None:
        return {}
    with sqlite3.connect(db_path) as conn:
        values = conn.execute(
            "SELECT peer_id, COUNT(*) FROM outbox WHERE state NOT IN ('acked','dead','expired') GROUP BY peer_id"
        ).fetchall()
    return {str(peer_id): int(depth) for peer_id, depth in sorted(values)}
