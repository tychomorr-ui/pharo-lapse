#!/usr/bin/env python3
"""Nexinus WireGuard signed-message proof tool.

Diagnostic only: uses separate test Ed25519 keys and a JSON format of its own.
It does not use the Messages page's IndexedDB keys or CID serializer.
The HTTP bytes are protected in transit only when the route really traverses
WireGuard. The script itself does not encrypt the application payload.
"""

import argparse
import base64
import hashlib
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROTOCOL = "nexinus-wg-signed-probe/1"
ACK_PROTOCOL = "nexinus-wg-signed-probe-ack/1"
MAX_BODY = 8192
SPKI_ED25519_PREFIX = bytes.fromhex("302a300506032b6570032100")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,47}$")


def state_root():
    return Path(os.environ.get("NEXINUS_WG_STATE", str(Path.home() / ".nexinus-wg-proof"))).expanduser()


def require_id(value):
    if not ID_RE.fullmatch(value):
        raise ValueError("peer IDs must be 1–48 letters, digits, dot, underscore, or hyphen")
    return value


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_openssl(args, *, input_bytes=None):
    if not shutil.which("openssl"):
        raise RuntimeError("OpenSSL CLI not found. Install OpenSSL, then rerun.")
    result = subprocess.run(["openssl", *args], input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError("OpenSSL failed: " + (detail or "command failed"))
    return result.stdout


def identity_paths(peer_id):
    peer_id = require_id(peer_id)
    d = state_root() / "identities"
    return d / f"{peer_id}.private.pem", d / f"{peer_id}.public.pem"


def trust_path(local_id, peer_id):
    return state_root() / "trusted" / require_id(local_id) / f"{require_id(peer_id)}.public.pem"


def identity_public_raw(peer_id):
    private, public = identity_paths(peer_id)
    if not private.is_file() or not public.is_file():
        raise FileNotFoundError(f"No test identity for {peer_id}; run: init {peer_id}")
    der = run_openssl(["pkey", "-pubin", "-in", str(public), "-outform", "DER"])
    if len(der) != 44 or not der.startswith(SPKI_ED25519_PREFIX):
        raise RuntimeError("Identity public key is not a 32-byte Ed25519 key")
    return der[-32:]


def public_raw_from_pem(pem):
    with tempfile.TemporaryDirectory(prefix="nexinus-key-") as td:
        p = Path(td) / "peer.pem"
        p.write_bytes(pem)
        der = run_openssl(["pkey", "-pubin", "-in", str(p), "-outform", "DER"])
    if len(der) != 44 or not der.startswith(SPKI_ED25519_PREFIX):
        raise ValueError("Expected a valid Ed25519 public key")
    return der[-32:]


def pem_from_raw(raw):
    if len(raw) != 32:
        raise ValueError("Ed25519 public key must be 32 bytes")
    der = SPKI_ED25519_PREFIX + raw
    b64 = base64.b64encode(der).decode("ascii")
    lines = "\n".join(b64[i:i + 64] for i in range(0, len(b64), 64))
    return f"-----BEGIN PUBLIC KEY-----\n{lines}\n-----END PUBLIC KEY-----\n".encode()


def b64decode(text):
    return base64.b64decode(text.encode("ascii"), validate=True)


def sign_bytes(peer_id, data):
    private, _ = identity_paths(peer_id)
    if not private.is_file():
        raise FileNotFoundError(f"No identity for {peer_id}; run init first")
    with tempfile.TemporaryDirectory(prefix="nexinus-sign-") as td:
        src, sig = Path(td) / "data.bin", Path(td) / "signature.bin"
        src.write_bytes(data)
        run_openssl(["pkeyutl", "-sign", "-inkey", str(private), "-rawin", "-in", str(src), "-out", str(sig)])
        return sig.read_bytes()


def verify_bytes(public_pem, data, signature):
    with tempfile.TemporaryDirectory(prefix="nexinus-verify-") as td:
        d = Path(td)
        pub, src, sig = d / "public.pem", d / "data.bin", d / "signature.bin"
        pub.write_bytes(public_pem)
        src.write_bytes(data)
        sig.write_bytes(signature)
        try:
            run_openssl(["pkeyutl", "-verify", "-pubin", "-inkey", str(pub), "-rawin", "-in", str(src), "-sigfile", str(sig)])
            return True
        except RuntimeError:
            return False


def ensure_private_dir(path):
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def cmd_init(args):
    peer_id = require_id(args.peer_id)
    priv, pub = identity_paths(peer_id)
    ensure_private_dir(priv.parent)
    if priv.exists() or pub.exists():
        raise FileExistsError(f"Identity already exists for {peer_id}; refusing to overwrite it")
    run_openssl(["genpkey", "-algorithm", "ED25519", "-out", str(priv)])
    priv.chmod(0o600)
    run_openssl(["pkey", "-in", str(priv), "-pubout", "-out", str(pub)])
    pub.chmod(0o600)
    raw = identity_public_raw(peer_id)
    print(f"Created TEST identity: {peer_id}")
    print("Private key saved locally with owner-only permissions; do not copy/share it.")
    print("Public key fingerprint (SHA-256):", hashlib.sha256(raw).hexdigest())
    print("PUBLIC_KEY_RAW_B64=" + base64.b64encode(raw).decode("ascii"))


def cmd_show_key(args):
    peer_id = require_id(args.peer_id)
    raw = identity_public_raw(peer_id)
    print("PEER_ID=" + peer_id)
    print("FINGERPRINT_SHA256=" + hashlib.sha256(raw).hexdigest())
    print("PUBLIC_KEY_RAW_B64=" + base64.b64encode(raw).decode("ascii"))


def cmd_trust(args):
    local_id, peer_id = require_id(args.local_id), require_id(args.peer_id)
    if local_id == peer_id:
        raise ValueError("local and peer IDs must differ")
    try:
        raw = b64decode(args.public_key_raw_b64)
    except Exception as e:
        raise ValueError("public key must be the PUBLIC_KEY_RAW_B64 value") from e
    if len(raw) != 32:
        raise ValueError("public key must decode to exactly 32 bytes")
    path = trust_path(local_id, peer_id)
    ensure_private_dir(path.parent)
    path.write_bytes(pem_from_raw(raw))
    path.chmod(0o600)
    print(f"Pinned {peer_id} for local identity {local_id}.")
    print("SHA-256 fingerprint:", hashlib.sha256(raw).hexdigest())


def load_trusted(local_id, peer_id):
    p = trust_path(local_id, peer_id)
    if not p.is_file():
        raise FileNotFoundError(f"No pinned key for {peer_id} under {local_id}; run trust")
    pem = p.read_bytes()
    raw = public_raw_from_pem(pem)
    return pem, raw


def make_envelope(sender_id, recipient_id, payload):
    sender_id, recipient_id = require_id(sender_id), require_id(recipient_id)
    if len(payload.encode("utf-8")) > 4096:
        raise ValueError("test payload must be 4096 bytes or less")
    body = {
        "protocol": PROTOCOL,
        "message_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "created_at": utc_now(),
        "payload": payload,
    }
    sig = sign_bytes(sender_id, canonical(body))
    raw = identity_public_raw(sender_id)
    envelope = {
        "body": body,
        "sender_public_key_raw_b64": base64.b64encode(raw).decode("ascii"),
        "signature_b64": base64.b64encode(sig).decode("ascii"),
    }
    return envelope


def stored_ids(local_id):
    path = state_root() / "inbox" / f"{require_id(local_id)}.jsonl"
    known = {}
    if not path.exists():
        return known
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            known[record["body"]["message_id"]] = record["body_sha256"]
        except Exception:
            continue
    return known


def send_json(handler, code, obj):
    data = canonical(obj)
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def build_ack(local_id, sender_id, message_id, body_digest, result):
    body = {
        "protocol": ACK_PROTOCOL,
        "message_id": message_id,
        "sender_id": local_id,
        "recipient_id": sender_id,
        "message_sha256": body_digest,
        "result": result,
        "received_at": utc_now(),
    }
    return {
        "body": body,
        "receiver_public_key_raw_b64": base64.b64encode(identity_public_raw(local_id)).decode("ascii"),
        "signature_b64": base64.b64encode(sign_bytes(local_id, canonical(body))).decode("ascii"),
    }


def make_server(local_id, expected_peer_id, bind, port):
    local_id, expected_peer_id = require_id(local_id), require_id(expected_peer_id)
    expected_pem, expected_raw = load_trusted(local_id, expected_peer_id)
    # Confirm that the receiver's own identity exists before opening a port.
    identity_public_raw(local_id)
    inbox_dir = state_root() / "inbox"
    ensure_private_dir(inbox_dir)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_POST(self):
            if self.path != "/inbox":
                send_json(self, 404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= MAX_BODY:
                    send_json(self, 413, {"error": "invalid body size"})
                    return
                envelope = json.loads(self.rfile.read(length).decode("utf-8"))
                body = envelope["body"]
                if not isinstance(body, dict) or body.get("protocol") != PROTOCOL:
                    raise ValueError("unsupported envelope")
                if body.get("sender_id") != expected_peer_id or body.get("recipient_id") != local_id:
                    raise ValueError("sender/recipient ID mismatch")
                raw_from_envelope = b64decode(envelope["sender_public_key_raw_b64"])
                if raw_from_envelope != expected_raw:
                    raise ValueError("sender key does not match pinned fingerprint")
                sig = b64decode(envelope["signature_b64"])
                if not verify_bytes(expected_pem, canonical(body), sig):
                    raise ValueError("Ed25519 signature verification failed")
                message_id = body.get("message_id")
                if not isinstance(message_id, str) or len(message_id) > 80:
                    raise ValueError("invalid message ID")
                payload = body.get("payload")
                if not isinstance(payload, str):
                    raise ValueError("payload must be text")
                digest = hashlib.sha256(canonical(body)).hexdigest()
                known = stored_ids(local_id)
                if message_id in known and known[message_id] != digest:
                    raise ValueError("message ID collision with different content")
                result = "duplicate-already-stored" if message_id in known else "stored"
                if result == "stored":
                    record = dict(envelope)
                    record["body_sha256"] = digest
                    record["stored_at"] = utc_now()
                    path = inbox_dir / f"{local_id}.jsonl"
                    with path.open("ab") as f:
                        f.write(canonical(record) + b"\n")
                        f.flush()
                        os.fsync(f.fileno())
                    try:
                        path.chmod(0o600)
                    except OSError:
                        pass
                print(f"VERIFIED message_id={message_id} from={expected_peer_id}")
                print("Payload:", payload)
                print("Body SHA-256:", digest)
                ack = build_ack(local_id, expected_peer_id, message_id, digest, result)
                send_json(self, 200, ack)
                self.server.valid_message.set()
            except Exception as e:
                print("REJECTED:", str(e))
                send_json(self, 400, {"error": str(e)})

    class OneMessageHTTPServer(HTTPServer):
        allow_reuse_address = True

    server = OneMessageHTTPServer((bind, port), Handler)
    server.timeout = 0.25
    server.valid_message = threading.Event()
    return server


def serve_one_valid(server):
    try:
        while not server.valid_message.is_set():
            server.handle_request()
    finally:
        server.server_close()


def transmit(host, port, envelope, timeout):
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    conn.request("POST", "/inbox", body=canonical(envelope), headers={"Content-Type": "application/json"})
    response = conn.getresponse()
    raw = response.read(MAX_BODY + 1)
    status = response.status
    conn.close()
    return status, raw


def verify_ack(local_id, peer_id, envelope, ack):
    body = ack["body"]
    peer_pem, peer_raw = load_trusted(local_id, peer_id)
    if b64decode(ack["receiver_public_key_raw_b64"]) != peer_raw:
        raise ValueError("receipt key does not match pinned recipient key")
    if not verify_bytes(peer_pem, canonical(body), b64decode(ack["signature_b64"])):
        raise ValueError("receipt Ed25519 signature verification failed")
    original = envelope["body"]
    digest = hashlib.sha256(canonical(original)).hexdigest()
    checks = (
        body.get("protocol") == ACK_PROTOCOL,
        body.get("message_id") == original.get("message_id"),
        body.get("sender_id") == peer_id,
        body.get("recipient_id") == local_id,
        body.get("message_sha256") == digest,
        body.get("result") in ("stored", "duplicate-already-stored"),
    )
    if not all(checks):
        raise ValueError("receipt fields do not match the sent message")
    return body, digest


def cmd_listen(args):
    server = make_server(args.local_id, args.expect_peer, args.bind, args.port)
    print(f"Listening once on {args.bind}:{args.port}/inbox; pinned sender={args.expect_peer}.", flush=True)
    print("This test listener accepts only a correctly signed message from the pinned key.", flush=True)
    serve_one_valid(server)


def cmd_send(args):
    local_id, peer_id = require_id(args.local_id), require_id(args.to_id)
    if not (1 <= args.port <= 65535):
        raise ValueError("port must be 1–65535")
    envelope = make_envelope(local_id, peer_id, args.message)
    print("Sending signed message_id:", envelope["body"]["message_id"])
    status, response = transmit(args.host, args.port, envelope, args.timeout)
    if status != 200:
        raise RuntimeError(f"receiver returned HTTP {status}: {response.decode('utf-8', 'replace')[:500]}")
    ack = json.loads(response.decode("utf-8"))
    body, digest = verify_ack(local_id, peer_id, envelope, ack)
    print("ACK VERIFIED: recipient signature and message binding are valid.")
    print("result:", body["result"])
    print("message_id:", body["message_id"])
    print("message_sha256:", digest)
    print("NOTE: this is the standalone probe format, not the browser app's CID/signature implementation.")


def cmd_selftest(_args):
    old = os.environ.get("NEXINUS_WG_STATE")
    with tempfile.TemporaryDirectory(prefix="nexinus-selftest-") as td:
        os.environ["NEXINUS_WG_STATE"] = td
        try:
            cmd_init(argparse.Namespace(peer_id="chromebook"))
            cmd_init(argparse.Namespace(peer_id="phone"))
            phone_raw = base64.b64encode(identity_public_raw("phone")).decode("ascii")
            chromebook_raw = base64.b64encode(identity_public_raw("chromebook")).decode("ascii")
            cmd_trust(argparse.Namespace(local_id="chromebook", peer_id="phone", public_key_raw_b64=phone_raw))
            cmd_trust(argparse.Namespace(local_id="phone", peer_id="chromebook", public_key_raw_b64=chromebook_raw))

            server = make_server("phone", "chromebook", "127.0.0.1", 0)
            port = server.server_address[1]
            thread = threading.Thread(target=serve_one_valid, args=(server,), daemon=True)
            thread.start()
            env = make_envelope("chromebook", "phone", "SELFTEST-ONE")
            status, response = transmit("127.0.0.1", port, env, 3)
            if status != 200:
                raise RuntimeError("selftest valid message was not accepted")
            ack_body, _ = verify_ack("chromebook", "phone", env, json.loads(response))
            thread.join(timeout=3)
            if not ack_body:
                raise RuntimeError("selftest receipt failed")
            print("SELFTEST PASS: signed envelope verified, stored, and signed receipt verified.")
            print("Scope: localhost only; this does not test the WireGuard route or web app.")
        finally:
            if old is None:
                os.environ.pop("NEXINUS_WG_STATE", None)
            else:
                os.environ["NEXINUS_WG_STATE"] = old


def build_parser():
    p = argparse.ArgumentParser(description="Signed-envelope proof over an already-working WireGuard path")
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("init", help="create a new local TEST Ed25519 identity")
    q.add_argument("peer_id")
    q.set_defaults(func=cmd_init)
    q = sub.add_parser("show-key", help="print public key only; safe to exchange out of band")
    q.add_argument("peer_id")
    q.set_defaults(func=cmd_show_key)
    q = sub.add_parser("trust", help="pin a peer's 32-byte raw public key")
    q.add_argument("local_id")
    q.add_argument("peer_id")
    q.add_argument("public_key_raw_b64")
    q.set_defaults(func=cmd_trust)
    q = sub.add_parser("listen", help="accept one valid signed message and return a signed receipt")
    q.add_argument("--local-id", required=True)
    q.add_argument("--expect-peer", required=True)
    q.add_argument("--bind", default="0.0.0.0")
    q.add_argument("--port", type=int, default=7777)
    q.set_defaults(func=cmd_listen)
    q = sub.add_parser("send", help="send a signed test message and verify the signed receipt")
    q.add_argument("--local-id", required=True)
    q.add_argument("--to-id", required=True)
    q.add_argument("--host", required=True)
    q.add_argument("--port", type=int, default=7777)
    q.add_argument("--message", default="NEXINUS-SIGNED-WG-TEST")
    q.add_argument("--timeout", type=float, default=8)
    q.set_defaults(func=cmd_send)
    q = sub.add_parser("selftest", help="test signing, verification, storage, and receipt on localhost")
    q.set_defaults(func=cmd_selftest)
    return p


def main():
    try:
        args = build_parser().parse_args()
        args.func(args)
    except KeyboardInterrupt:
        print("Stopped.", file=sys.stderr)
        return 130
    except Exception as e:
        print("ERROR:", str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
