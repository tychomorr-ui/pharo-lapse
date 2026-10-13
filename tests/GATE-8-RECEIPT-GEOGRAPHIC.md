# GATE 8 — GEOGRAPHIC DISTRIBUTION RECEIPT

**Date:** 13 October 2026
**Result:** PASS

## Topology
- Hub:    DigitalOcean SFO2 (San Francisco), 10.9.0.1, 165.227.29.23
- Node A: Chromebook Penguin (Ukiah, California), 10.9.0.2
- Node B: Android phone (Ukiah, California), 10.9.0.3
- Node C: DigitalOcean FRA1 (Frankfurt, Germany), 10.9.0.4, 134.209.243.197

## Frankfurt WireGuard public key
HBXaCk8mNKa1l1zLqYfvfZXxJbNTzgISjevh0P8X+Xk=

## Distance
- Ukiah to San Francisco:      ~200 km
- San Francisco to Frankfurt:  ~9,100 km
- Total one-way:               ~9,300 km
- Round trip:                  ~18,600 km

## Transport
- WireGuard overlay, port 443/udp
- Hub forwards between all peers
- Ocean crossing confirmed by round-trip latency

## Ping measurements (Penguin -> Frankfurt)
min/avg/max/mdev = 263.530/303.760/344.533/31.297 ms
packets: 4 transmitted, 4 received, 0% loss

## Signed message test
- Sender:     Frankfurt (10.9.0.4)
- Recipient:  Penguin (10.9.0.2)
- Message ID: 52caffbd-acf5-4bd4-990d-c4b49bae2b33
- Body SHA-256: 35cfeb56a453d2213ab8ede1bfa38b62c2080af5ed3503a5bbd68bd97c576029
- Listener log: NEW 52caffbd-... 35cfeb56... at 2026-10-13T12:11:56
- Sender result: ACKED

## What this proves
- Pharo-Lapse delivers signed messages across continents
- The hub relays without any application logic
- Store-and-forward works at intercontinental distance
- The protocol is geographically distributed
- The Pin + CID + signature verification chain holds across an ocean

## Limitations (honest)
- Hub and Frankfurt node are rented DigitalOcean droplets, not
  sovereign operator hardware
- Two physical client devices (Penguin + phone) plus one remote server
- Frankfurt node is a VPS, not operator-owned
- No three-way multi-region message yet (Frankfurt to phone tested
  only via direct peer test, not as a relayed mesh test)

## Gate Ladder status
- Gate 3: HTTP over tunnel, no internet   — PASS
- Gate 4: Signed envelope + signed ack    — PASS
- Gate 5: Store-and-forward + restart     — PASS
- Gate 6: Exactly-once delivery           — PASS
- Gate 7: Three-device mesh               — PASS
- Gate 8: Geographic distribution         — PASS
