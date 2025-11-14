import requests
from . import ProtocolHandler

class HTTPHandler(ProtocolHandler):
    def __init__(self, url):
        self.url = url
        self.session = None

    def connect(self):
        self.session = requests.Session()
        print(f"Connected to {self.url}")

    def receive_data(self):
        if self.session:
            response = self.session.get(self.url)
            return response.text
        return None

    def disconnect(self):
        if self.session:
            self.session.close()
            print("Disconnected")