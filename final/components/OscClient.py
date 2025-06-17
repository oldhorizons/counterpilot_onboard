from pythonosc import udp_client
from constants import osc_ip, osc_port

class OscClient:
    def __init__(self, osc_ip, osc_port):
        self.oscClient = udp_client.SimpleUDPClient(osc_ip, osc_port)
        print(f"Initialised OSC client to {osc_ip}:{osc_port}")

    def send_pupil(self, id, x, y, d):
        self.oscClient.send_message(f"/cue/eye{id}D/name", d)
        self.oscClient.send_message(f"/cue/eye{id}X/name", x)
        self.oscClient.send_message(f"/cue/eye{id}Y/name", y)
        print(f"sent d{d}x{x}y{y}")