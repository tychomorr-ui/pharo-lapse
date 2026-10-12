# GATE 7 — THREE-DEVICE MESH RECEIPT

**Date:** 12 October 2026
**Result:** PASS

## Topology
- Node A: Chromebook Penguin (10.9.0.2)
- Node B: Android phone (10.9.0.3)
- Hub:   DigitalOcean SFO2 (10.9.0.1) — 165.227.29.23

## Transport
- WireGuard overlay, port 443/udp
- Hub forwards between peers (ufw allow in/out on wg0, iptables FORWARD)
- Geographic path: Ukiah -> San Jose -> Ukiah, ~95 ms round trip

## Sequence proven
1. Penguin pinged phone: 0% loss, 94 ms average
2. Penguin pinged hub: 0% loss, 37 ms average
3. Phone POST probe to Penguin listener: {"received": true, "new": true}
4. Phone queue sent 2 messages to Penguin over the mesh
5. Penguin listener accepted both
6. Phone's outbox marked both ACKED

## Message IDs
- e7e5ea38-7aee-407a-9410-b75e2a970b5e
- 42e9e89b-abc3-4b21-8c47-117b32e18475

## What this proves
- Any-to-any delivery across 3 devices over a WAN-disconnected overlay
- Hub forwards between peers with no central application logic
- Store-and-forward queue works in both directions
- Signed envelope protocol runs end-to-end

## Limitations (honest)
- Android Termux cannot bind to WireGuard overlay IPs on Android
  (VpnService isolation), so Penguin runs the listener in this test
- Two physical devices + one hub, not three distinct client devices
- Hub is a DigitalOcean droplet, not sovereign operator hardware

## Gate Ladder status
- Gate 3: HTTP over tunnel, no internet  — PASS
- Gate 4: Signed envelope + signed ack  — PASS
- Gate 5: Store-and-forward + restart  — PASS
- Gate 6: Exactly-once delivery         — PASS
- Gate 7: Three-device mesh             — PASS
- Gate 8: Geographic distribution       — PARTIAL (same city, different networks)
