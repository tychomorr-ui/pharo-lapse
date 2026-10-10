# NEXINUS SOVEREIGN OVERLAY — GATE 3 RECEIPT (WAN-DISCONNECTED)

**Date:** 2026-10-09
**Test:** Signed-message transport over WireGuard with public internet unavailable
**Result:** PASS

## Environment
- Phone: hotspot ON, mobile data OFF
- Chromebook: connected to phone's hotspot, no internet access
- Network gateway: phone hotspot IP
- Transport: WireGuard (userspace implementation inside Penguin container)

## Tunnel Verification
- Handshake: confirmed (latest handshake within 30 seconds)
- Bytes: 604 B received, 6.61 KiB sent
- Interface: wg-nexinus @ 10.9.0.2/32
- Peer: 10.9.0.1 (phone)

## Transport Verification
- Request: HTTP GET from Penguin (10.9.0.2) to phone (10.9.0.1:7777)
- Response: HTTP/1.0 200 OK, 568 bytes
- Server: SimpleHTTP/0.6 Python/3.13.13 (on phone)
- Confirmed on both endpoints

## Key Findings
- A real HTTP request crossed the WireGuard tunnel between two independently
  owned devices.
- Public internet access was unavailable on the network used for the test.
- Mobile data was disabled on the phone; hotspot was the only active interface.
- No cloud relay, no vendor, no third-party service was used.

## Limitations (Honest)
- This is local-network messaging without public internet.
- It is NOT a radio-silent mesh, satellite, or carrier-independent test.
- Signed-ack protocol across the tunnel remains to be captured.
- The scenario is two devices in proximity, not geographically distributed.
