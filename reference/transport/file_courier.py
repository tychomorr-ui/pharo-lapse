"""File courier transport. Writes envelopes to a directory; a human or
USB stick moves them to the peer. The queue calls send() and listen()
without caring how the bytes actually move."""
import json
import os
import time
from pathlib import Path

class FileCourier:
    def __init__(self, outbox_dir, inbox_dir):
        self.outbox = Path(outbox_dir)
        self.inbox = Path(inbox_dir)
        self.outbox.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)

    def send(self, peer_id, envelope_json):
        target = self.outbox / f"{int(time.time())}-{peer_id}.json"
        target.write_text(envelope_json)
        return {"status": "queued", "path": str(target)}

    def listen(self):
        for f in sorted(self.inbox.glob("*.json")):
            envelope = json.loads(f.read_text())
            f.unlink()
            yield envelope
