from abc import ABC, abstractmethod
from Map import Map
class Device(ABC):

    @abstractmethod
    def __init__(self, dev_id, data_rate, payload, interval):
        super().__init__()

    @abstractmethod
    def createFrame(self):
        pass

    def generatePosition(self):
        self.position = Map.get_position()

    @staticmethod
    def get_off_period(t_air, dc):
        """Return minimum off-period for duty cycle 1%"""
        return round(t_air * (1.0 / dc - 1))