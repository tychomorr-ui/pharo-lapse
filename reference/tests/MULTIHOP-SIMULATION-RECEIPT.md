# MULTI-HOP RELAY SIMULATION RECEIPT

**Date:** 14 October 2026
**Result:** PASS

## Topology
- Node A: Chromebook Penguin
- Node B: intermediate relay
- Node C: destination
- A cannot reach C directly. B is the only path.

## Sequence
1. A builds envelope for C: msg_id 0001
2. A sends to B (its only reachable peer)
3. B receives, confirms it is not the recipient
4. B checks route_history for loops (none)
5. B forwards to C, appending itself to route_history
6. C receives, confirms it is the recipient
7. C delivers

## Output
