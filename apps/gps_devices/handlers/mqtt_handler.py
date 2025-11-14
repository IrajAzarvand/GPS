import paho.mqtt.client as mqtt
from . import ProtocolHandler

class MQTTHandler(ProtocolHandler):
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        print(f"Connected to MQTT broker {self.broker}:{self.port}")

    def receive_data(self):
        def on_message(client, userdata, msg):
            return msg.payload.decode('utf-8')

        self.client.on_message = on_message
        self.client.subscribe(self.topic)
        # For simplicity, wait for a message (this is blocking for demo)
        self.client.loop(10)  # Wait up to 10 seconds for a message
        # Note: In real use, this should be non-blocking

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT broker")