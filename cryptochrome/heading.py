"""Deterministic weighted-intersection next-hop selection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Heading:
    selected_peer: str | None
    candidates: tuple[str, ...]
    scores: dict[str, int]
    reason: str


def synthesize_heading(
    *,
    reachable_peer_ids: set[str],
    arrival_history: Mapping[str, Sequence[str]],
    queue_depths: Mapping[str, int],
    route_history: Sequence[str] = (),
    recipient_peer_id: str | None = None,
) -> Heading:
    """Choose a next hop from three observable signals.

    Score = reachability (4) + prior arrivals (2) + queued work (1). Ties are
    broken lexicographically. Already visited peers and the final recipient are
    excluded from transit selection; the recipient remains eligible when it is
    the only direct destination.
    """
    visited = set(route_history)
    candidates = set(reachable_peer_ids) - visited
    if recipient_peer_id is not None:
        candidates.discard(recipient_peer_id)
    scores = {
        peer_id: 4 + 2 * len(arrival_history.get(peer_id, ())) + int(queue_depths.get(peer_id, 0))
        for peer_id in candidates
    }
    ordered = tuple(sorted(scores, key=lambda peer_id: (-scores[peer_id], peer_id)))
    if not ordered:
        return Heading(None, (), {}, "no reachable unvisited transit peer")
    return Heading(ordered[0], ordered, scores, "weighted intersection")
