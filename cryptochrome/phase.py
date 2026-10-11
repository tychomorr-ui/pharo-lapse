"""Reachability-derived DAY/NIGHT/TWILIGHT phase computation."""
from __future__ import annotations

from enum import Enum
from typing import Mapping


class Phase(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    TWILIGHT = "TWILIGHT"


def compute_phase(reachable: int, pinned: int) -> Phase:
    if pinned < 0 or reachable < 0 or reachable > pinned:
        raise ValueError("reachable and pinned counts must satisfy 0 <= reachable <= pinned")
    if pinned == 0:
        return Phase.NIGHT
    ratio = reachable / pinned
    if ratio >= 0.5:
        return Phase.DAY
    if ratio < 0.25:
        return Phase.NIGHT
    return Phase.TWILIGHT


def phase_from_peers(peer_states: Mapping[str, object], pinned_peer_ids: set[str]) -> Phase:
    reachable = sum(1 for peer_id in pinned_peer_ids if getattr(peer_states.get(peer_id), "reachable", False))
    return compute_phase(reachable, len(pinned_peer_ids))
