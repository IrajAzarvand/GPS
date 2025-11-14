from .tcp_handler import TCPHandler
from .mqtt_handler import MQTTHandler
from .http_handler import HTTPHandler

class ProtocolFactory:
    @staticmethod
    def create_handler(protocol_type, **kwargs):
        if protocol_type.lower() == 'tcp':
            return TCPHandler(kwargs.get('host'), kwargs.get('port'))
        elif protocol_type.lower() == 'mqtt':
            return MQTTHandler(kwargs.get('broker'), kwargs.get('port'), kwargs.get('topic'))
        elif protocol_type.lower() == 'http':
            return HTTPHandler(kwargs.get('url'))
        else:
            raise ValueError(f"Unknown protocol type: {protocol_type}")