import socket
import threading
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.gps_devices.models import RawGPSData, Device, Protocol

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start GPS data receiver on port 5000'

    def handle(self, *args, **options):
        self.stdout.write('Starting GPS receiver on port 5000...')
        server = GPSReceiver()
        server.start()

class GPSReceiver:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f'GPS receiver listening on {self.host}:{self.port}')

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                logger.info(f'Connection from {address}')
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.start()
        except KeyboardInterrupt:
            logger.info('Shutting down GPS receiver')
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()
            if data:
                logger.info(f'Received data from {address}: {data}')
                self.save_raw_data(data, address[0])
        except Exception as e:
            logger.error(f'Error handling client {address}: {e}')
        finally:
            client_socket.close()

    def save_raw_data(self, data, ip_address):
        try:
            # Get or create a default protocol
            protocol, created = Protocol.objects.get_or_create(
                name='Unknown TCP',
                defaults={
                    'protocol_type': 'tcp',
                    'description': 'Default protocol for unknown GPS devices',
                    'default_port': 5000,
                }
            )

            # Save raw data without device for now
            raw_data = RawGPSData.objects.create(
                device=None,
                protocol=protocol,
                raw_data=data,
                ip_address=ip_address,
            )
            logger.info(f'Saved raw GPS data: {raw_data.id}')
        except Exception as e:
            logger.error(f'Error saving raw data: {e}')