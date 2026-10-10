# NEXINUS SOVEREIGN OVERLAY — GATE 4 RECEIPT
## Signed envelope + signed ack over WAN-disconnected WireGuard

**Date:** 2026-10-09
**Result:** PASS

## Environment
- Phone: hotspot ON, mobile data OFF
- Chromebook: connected to hotspot, no internet access
- No cloud relay, no vendor, no third-party service

## Tunnel
- Interface: wg-nexinus (userspace WireGuard in Penguin)
- Penguin: 10.9.0.2/32
- Phone: 10.9.0.1:51820
- Handshake: fresh (latest handshake: Now)
- Persistent keepalive: every 25 seconds

## Signed Exchange
- Message ID: 37f28fa7-b820-4df5-8cda-8dec89033428
- Sender: penguin (Ed25519 signed envelope)
- Recipient: phone
- Recipient verification: signature valid, pinned key matched
- Payload SHA-256: 8c340fc0253c09f21688641442d23fa184e7f540fce39f97476b2a9ab3ce778e
- Recipient returned signed receipt
- Sender verified receipt: signature valid, pinned key matched

## What This Proves
- A signed Ed25519 envelope crossed a self-hosted encrypted WireGuard tunnel
- Recipient verified sender identity against a pinned public key
- Recipient returned a signed receipt that the sender also verified
- The full exchange occurred with public internet unavailable

## Limitations (Honest)
- Two devices in the same physical location (not geographically distributed)
- Not radio-silent, not satellite, not carrier-independent
- Store-and-forward not tested
- Multihop relay not tested
- Standalone probe format, not the browser app's CID implementation
