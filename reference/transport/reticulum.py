"""Reticulum transport. RNS handles interface abstraction, routing,
and multi-hop. Pharo-Lapse carries signed envelopes on top."""
import RNS

class ReticulumTransport:
    def __init__(self, destination_hash):
        self.reticulum = RNS.Reticulum()
        self.identity = RNS.Identity()
        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            "pharo",
            "lapse",
        )
        self.peer_hash = destination_hash
        self.destination.set_link_established_callback(self._on_link)

    def send(self, peer_id, envelope_json):
        peer_dest = RNS.Destination(
            None, RNS.Destination.OUT, RNS.Destination.SINGLE,
            "pharo", "lapse", bytes.fromhex(peer_id)
        )
        RNS.Packet(peer_dest, envelope_json.encode()).send()
        return {"status": "sent", "peer": peer_id}

    def _on_link(self, link):
        link.set_packet_callback(self._on_packet)

    def _on_packet(self, message, packet):
        yield json.loads(message.decode())
