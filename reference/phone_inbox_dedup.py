import http.server, sqlite3, json, hashlib, os
from datetime import datetime, timezone

DB = os.path.expanduser('~/phone_inbox.db')

def init_db():
    c = sqlite3.connect(DB)
    c.execute('CREATE TABLE IF NOT EXISTS inbox (msg_id TEXT PRIMARY KEY, received_at TEXT, sha256 TEXT, ack_json TEXT)')
    c.commit()
    return c

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(s):
        n = int(s.headers.get("Content-Length", "0") or 0)
        body = s.rfile.read(n)
        try:
            obj = json.loads(body)
        except Exception:
            obj = {}
        msg_id = obj.get("msg_id", "unknown")
        sha = hashlib.sha256(body).hexdigest()
        c = init_db()
        row = c.execute('SELECT ack_json FROM inbox WHERE msg_id=?', (msg_id,)).fetchone()
        if row:
            ack_json = row[0]
            print(f"DUP {msg_id} {sha}", flush=True)
        else:
            ack_json = json.dumps({"received": True, "msg_id": msg_id, "sha256": sha, "new": True})
            c.execute('INSERT INTO inbox (msg_id, received_at, sha256, ack_json) VALUES (?, ?, ?, ?)',
                      (msg_id, datetime.now(timezone.utc).isoformat(), sha, ack_json))
            c.commit()
            print(f"NEW {msg_id} {sha}", flush=True)
        out = ack_json.encode()
        s.send_response(200)
        s.send_header("Content-Type", "application/json")
        s.send_header("Content-Length", str(len(out)))
        s.end_headers()
        s.wfile.write(out)

init_db()
print("phone_inbox_dedup listening on 0.0.0.0:7777", flush=True)
http.server.HTTPServer(("0.0.0.0", 7777), H).serve_forever()
