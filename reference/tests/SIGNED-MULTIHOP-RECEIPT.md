# Signed Multi-Hop Verification Receipt

**Date:** 2026-10-14
**Result:** PASS
**Implementation:** `reference/envelope_v3.py`, `reference/forward_signed.py`

## Exact test command

```bash
python3 -m unittest discover -s reference/tests -p 'test_signed_multihop.py' -v
```

## Exact test output

```text
test_invalid_relay_signature_rejected (test_signed_multihop.SignedMultihopTests.test_invalid_relay_signature_rejected) ... ok
test_loop_a_b_c_b_dropped (test_signed_multihop.SignedMultihopTests.test_loop_a_b_c_b_dropped) ... ok
test_missing_relay_signature_rejected (test_signed_multihop.SignedMultihopTests.test_missing_relay_signature_rejected) ... ok
test_replay_at_b_is_deduplicated (test_signed_multihop.SignedMultihopTests.test_replay_at_b_is_deduplicated) ... ok
test_sign_forward_a_b_c_verify_at_c (test_signed_multihop.SignedMultihopTests.test_sign_forward_a_b_c_verify_at_c) ... ok
test_tamper_body_at_b_rejected_at_c (test_signed_multihop.SignedMultihopTests.test_tamper_body_at_b_rejected_at_c) ... ok
test_tamper_route_history_at_b_rejected_at_c (test_signed_multihop.SignedMultihopTests.test_tamper_route_history_at_b_rejected_at_c) ... ok
test_ttl_exceeded (test_signed_multihop.SignedMultihopTests.test_ttl_exceeded) ... ok
----------------------------------------------------------------------
Ran 8 tests in 0.014s
OK
```

The suite was also syntax-checked with:

```bash
python3 -m py_compile reference/envelope_v3.py reference/forward_signed.py reference/tests/test_signed_multihop.py
```

## A-to-B-to-C signed run

Exact command used for the receipt run:

```bash
python3 - <<'PY'
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reference.envelope_v3 import build_envelope, forward_signed, verify_envelope

keys = {p: Ed25519PrivateKey.generate() for p in ('node-a','node-b','node-c')}
public = {p: k.public_key() for p,k in keys.items()}
body = 'SIGNED-MULTIHOP-RECEIPT-001'
env = build_envelope('node-a', 'node-c', body, keys['node-a'], msg_id='signed-receipt-0001')
verify_envelope(env, public)
b = forward_signed(env, 'node-b', keys['node-b'], 'node-c', public)
verify_envelope(b, public, expected_recipient='node-c')
PY
```

Observed output:

```text
A BUILD msg_id= signed-receipt-0001
A SIGNATURE VERIFIED=PASS
B FORWARD route_history= ['node-a', 'node-b']
B ORIGIN SIGNATURE VERIFIED=PASS
B RELAY SIGNATURE VERIFIED=PASS
C FINAL VERIFY=PASS
MESSAGE_ID= signed-receipt-0001
BODY_SHA256= ed24cbb27e086b26bfb23eaf4fdd8c613c01adda4b4cda0093686366f062c67d
ROUTE_HISTORY= node-a -> node-b
SIGNATURES_VERIFIED= 2
CURRENT_CID= f6c212876a105cae1ed27c98fb91fa9a1f1ebf88b0c606801fd31209e6d90b12
```

## Assertions covered

1. Origin signs and verifies across A → B → C.
2. Body tampering is rejected.
3. Route-history tampering is rejected.
4. Replay at B is deduplicated by `(msg_id, origin_cid)`.
5. A repeated relay route is rejected.
6. The hop limit is enforced.
7. A missing relay signature is rejected.
8. An invalid relay signature is rejected.

## Boundary

This is an executable cryptographic and forwarding test using generated Ed25519 identities. It does not claim a live DigitalOcean or WireGuard run, hardware-backed key storage, or production durable SQLite relay persistence. Those remain deployment and integration work.
