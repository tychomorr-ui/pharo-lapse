"""WireGuard peer-state sensor with an injectable command source."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class PeerState:
    peer_id: str
    endpoint: str | None
    latest_handshake: int
    rx_bytes: int
    tx_bytes: int

    @property
    def reachable(self) -> bool:
        return self.latest_handshake > 0


def parse_wg_dump(lines: Iterable[str]) -> dict[str, PeerState]:
    """Parse `wg show all dump` rows using peer_id as the final stable column.

    The normal WireGuard dump has interface rows followed by peer rows. For a
    deterministic node registry, callers may provide rows with a trailing peer_id:
    public_key preshared endpoint allowed_ips latest_handshake rx tx peer_id.
    """
    states: dict[str, PeerState] = {}
    for raw in lines:
        fields = raw.rstrip("\n").split("\t")
        if len(fields) < 8:
            continue
        public_key, _psk, endpoint, _allowed, handshake, rx, tx, peer_id = fields[-8:]
        try:
            state = PeerState(str(peer_id), None if endpoint == "(none)" else endpoint,
                              int(handshake), int(rx), int(tx))
        except ValueError:
            continue
        states[state.peer_id] = state
    return dict(sorted(states.items()))


def read_peer_state(
    command: Callable[[], str] | None = None,
    *,
    dump: str | None = None,
) -> dict[str, PeerState]:
    if dump is None:
        if command is not None:
            dump = command()
        else:
            dump = subprocess.run(
                ["wg", "show", "all", "dump"], capture_output=True, text=True, check=True
            ).stdout
    return parse_wg_dump(dump.splitlines())
