from abc import ABC, abstractmethod

class ProtocolHandler(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass