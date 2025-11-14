import socket
from . import ProtocolHandler

class TCPHandler(ProtocolHandler):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

    def receive_data(self):
        if self.sock:
            data = self.sock.recv(1024)
            return data.decode('utf-8')
        return None

    def disconnect(self):
        if self.sock:
            self.sock.close()
            print("Disconnected")