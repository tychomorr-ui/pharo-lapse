"""LoRa transport via Meshtastic."""
import json
import meshtastic
import meshtastic.serial_interface

class LoRaTransport:
    def __init__(self, device_path=None):
        if device_path:
            self.iface = meshtastic.serial_interface.SerialInterface(devPath=device_path)
        else:
            self.iface = meshtastic.serial_interface.SerialInterface()

    def send(self, peer_id, envelope_json):
        # Meshtastic has a ~200 byte text limit; send as a single packet
        # For larger envelopes, chunk and reassemble.
        self.iface.sendText(envelope_json, destinationId=peer_id)
        return {"status": "sent", "peer": peer_id}

    def listen(self):
        def on_receive(packet, interface):
            if "decoded" in packet and "text" in packet["decoded"]:
                try:
                    envelope = json.loads(packet["decoded"]["text"])
                    yield envelope
                except json.JSONDecodeError:
                    pass

        meshtastic.pub.subscribe(on_receive, "meshtastic.receive.text")
        # Note: this is a publish-subscribe model; in production use a queue
