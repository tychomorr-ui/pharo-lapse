# WAN Outage and Recovery Receipt

**Date:** 2026-10-13
**Operator:** Tyler Morris
**Client:** Chromebook Penguin
**Destination:** Frankfurt Linux peer (10.9.0.4)
**Result:** PASS

## Verified sequence

- Penguin WireGuard tunnel was brought down.
- 10.9.0.1 became unreachable with 100% packet loss.
- Two messages were queued while offline.
- Delivery failed while offline without message loss.
- The queue process was terminated.
- Both pending messages survived process termination.
- WireGuard was restored with a fresh handshake.
- Frankfurt received and acknowledged both messages.

## Message IDs

- 1877f94e-b96c-46a0-8924-ace2d532c54a
- 08af7da9-f193-4dfd-be3e-e795b61e41f2

## Frankfurt listener evidence

NEW 1877f94e-b96c-46a0-8924-ace2d532c54a 5a8c20ce1061d7fd2b6ab0a2ba904cd501cc3f70ee7c61d0d2b7a8687a5cf7cc
NEW 08af7da9-f193-4dfd-be3e-e795b61e41f2 ca98173d8bbdbcce12a629a3110b8d3b377a4554d75ccd3e51a00efcbee77864

## Recovery evidence

ACKED 1877f94e-b96c-46a0-8924-ace2d532c54a
ACKED 08af7da9-f193-4dfd-be3e-e795b61e41f2
acked: 2

Second delivery pass: acked: 2; no additional delivery occurred.

## Final status

- Queue survived process death: PASS
- Offline delivery failed without loss: PASS
- WireGuard recovery: PASS
- Post-recovery delivery: PASS
- Duplicate delivery prevented: PASS
- Overall result: PASS

## Limitations

- Recovery destination was Frankfurt, not the Android phone.
- Android inbound listening remained unavailable.
- This test did not demonstrate multi-hop relay behavior.
