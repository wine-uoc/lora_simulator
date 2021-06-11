from abc import ABC, abstractmethod
from Map import Map
from Modulation import Modulation

class Device(ABC):

    @abstractmethod
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__()
        self.modulation = Modulation(data_rate)
        self.dev_id = dev_id
        self.data_rate = data_rate
        self.payload_size = payload_size
        self.time_mode = time_mode

    @abstractmethod
    def createFrame(self):
        pass

    def generatePosition(self):
        self.position = Map.get_position()

    def get_off_period(t_air, dc):
        """Return minimum off-period for duty cycle 1%"""
        return round(t_air * (1.0 / dc - 1))

    #Generate the next time for transmission
    def next_time(self):