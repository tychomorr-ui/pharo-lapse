#!/usr/bin/env python3
"""NEXINUS QUEUE — Pharo gap store-and-forward over WireGuard."""
import json, os, sqlite3, sys, time, uuid, random, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.request, urllib.error

HOME = Path.home()
DB = HOME / ".nexinus-queue.db"
IDENT = HOME / ".nexinus-wg-proof"
RETRY_DELAYS = [30, 60, 120, 240, 480, 600]
MAX_ATTEMPTS = 20
JITTER = 0.10


def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()


def open_db():
    conn = sqlite3.connect(str(DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS outbox (
          msg_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, peer_id TEXT NOT NULL,
          envelope_json TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
          attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at TEXT,
          expires_at TEXT, last_error TEXT, acked_at TEXT, ack_json TEXT
        );
        CREATE TABLE IF NOT EXISTS inbox (
          msg_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, peer_id TEXT NOT NULL,
          envelope_json TEXT NOT NULL, body_sha256 TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS peers (
          peer_id TEXT PRIMARY KEY, host TEXT NOT NULL, port INTEGER NOT NULL,
          public_key_b64 TEXT NOT NULL, last_seen TEXT
        );
    """)
    conn.commit()
    return conn


def recover(conn):
    conn.execute("UPDATE outbox SET state='pending', last_error='recovered from crash' WHERE state='inflight'")
    conn.execute("UPDATE outbox SET state='expired' WHERE state='pending' AND expires_at IS NOT NULL AND expires_at < ?", (iso_now(),))
    conn.commit()


def next_delay(attempt):
    base = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
    return int(base + random.uniform(-base * JITTER, base * JITTER))


def local_id():
    p = IDENT / "local_id"
    return p.read_text().strip() if p.exists() else "penguin"


def enqueue(conn, peer_id, body, ttl_hours=72):
    msg_id = str(uuid.uuid4())
    envelope = {
        "msg_id": msg_id, "created_at": iso_now(),
        "sender_peer_id": local_id(), "recipient_peer_id": peer_id,
        "body": body, "type": "message"
    }
    expires = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute("""INSERT INTO outbox
        (msg_id, created_at, peer_id, envelope_json, state, next_attempt_at, expires_at)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
        (msg_id, envelope["created_at"], peer_id, json.dumps(envelope), iso_now(), expires))
    conn.commit()
    print(f"QUEUED {msg_id}")
    return msg_id


def attempt_delivery(conn, row):
    msg_id, peer_id, envelope_json, attempts = row
    peer = conn.execute("SELECT host, port FROM peers WHERE peer_id=?", (peer_id,)).fetchone()
    if not peer:
        conn.execute("UPDATE outbox SET state='dead', last_error='no peer record' WHERE msg_id=?", (msg_id,))
        conn.commit()
        return "dead"
    host, port = peer
    conn.execute("UPDATE outbox SET state='inflight' WHERE msg_id=?", (msg_id,))
    conn.commit()
    req = urllib.request.Request(
        f"http://{host}:{port}/inbox",
        data=envelope_json.encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        from http.client import IncompleteRead
        with urllib.request.urlopen(req, timeout=30) as r:
            try:
                raw = r.read()
            except IncompleteRead as ir:
                raw = ir.partial
            ack = json.loads(raw)
        conn.execute("""UPDATE outbox SET state='acked', acked_at=?, ack_json=?
            WHERE msg_id=?""", (iso_now(), json.dumps(ack), msg_id))
        conn.commit()
        print(f"ACKED {msg_id}")
        return "acked"
    except Exception as e:
        attempts += 1
        if attempts >= MAX_ATTEMPTS:
            conn.execute("UPDATE outbox SET state='dead', attempts=?, last_error=? WHERE msg_id=?",
                (attempts, str(e), msg_id))
            conn.commit()
            print(f"DEAD {msg_id} after {attempts} attempts")
            return "dead"
        delay = next_delay(attempts)
        nxt = (datetime.now(timezone.utc) + timedelta(seconds=delay)).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn.execute("""UPDATE outbox SET state='pending', attempts=?, next_attempt_at=?,
            last_error=? WHERE msg_id=?""", (attempts, nxt, str(e), msg_id))
        conn.commit()
        print(f"RETRY {msg_id} in {delay}s (attempt {attempts})")
        return "pending"


def deliver_loop(conn, once=False):
    while True:
        now = iso_now()
        rows = conn.execute("""SELECT msg_id, peer_id, envelope_json, attempts FROM outbox
            WHERE state='pending' AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
            ORDER BY created_at LIMIT 10""", (now,)).fetchall()
        if not rows:
            if once:
                return
            time.sleep(5)
            continue
        for row in rows:
            attempt_delivery(conn, row)
        if once:
            return


def cmd_help():
    print("""nexinus_queue — Pharo gap store-and-forward

Usage:
  python3 nexinus_queue.py peer <peer_id> <host> <port> <pubkey_b64>
  python3 nexinus_queue.py add <peer_id> "<body>"
  python3 nexinus_queue.py deliver            # loop forever
  python3 nexinus_queue.py deliver --once     # one pass
  python3 nexinus_queue.py status
  python3 nexinus_queue.py pending
  python3 nexinus_queue.py inbox
""")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "help":
        cmd_help()
        sys.exit(0)
    conn = open_db()
    recover(conn)
    if cmd == "add":
        enqueue(conn, sys.argv[2], sys.argv[3])
    elif cmd == "peer":
        conn.execute("INSERT OR REPLACE INTO peers VALUES (?,?,?,?,?)",
            (sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], iso_now()))
        conn.commit()
        print(f"PEER {sys.argv[2]} -> {sys.argv[3]}:{sys.argv[4]}")
    elif cmd == "deliver":
        deliver_loop(conn, once=("--once" in sys.argv))
    elif cmd == "status":
        for r in conn.execute("SELECT state, COUNT(*) FROM outbox GROUP BY state"):
            print(f"{r[0]}: {r[1]}")
    elif cmd == "pending":
        for r in conn.execute("SELECT msg_id, peer_id, state, attempts, last_error FROM outbox WHERE state!='acked'"):
            print(r)
    elif cmd == "inbox":
        for r in conn.execute("SELECT msg_id, received_at, peer_id, body_sha256 FROM inbox ORDER BY received_at DESC LIMIT 20"):
            print(r)
    else:
        cmd_help()
