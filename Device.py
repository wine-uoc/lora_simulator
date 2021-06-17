import logging
from abc import ABC, abstractmethod
from Map import Map
from Modulation import Modulation
from Map import Map
from Frame import Frame
import numpy as np
import random

logger = logging.getLogger(__name__)

class Device(ABC):

    @abstractmethod
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__()
        self.modulation = Modulation(data_rate)
        self.dev_id = dev_id
        self.data_rate = data_rate
        self.payload_size = payload_size
        self.interval = interval
        self.time_mode = time_mode

        # The list of frames transmitted for frame traceability and metrics computation
        self.frame_list = []

        self._generate_position()

    @abstractmethod
    def create_frame(self):
        pass

    @abstractmethod
    def _compute_toa(self):
        pass

    def _generate_position(self):
        self.position = Map.get_position()

    def get_modulation_data (self):
        return self.modulation.get_data()

    def get_dev_id(self):
        return self.dev_id

    def get_data_rate(self):
        return self.data_rate

    def get_payload_size(self):
        return self.payload_size

    def get_interval(self):
        return self.interval

    def get_time_mode(self):
        return self.time_mode

    def get_position(self):
        return self.position

    def get_frame_list_length(self):
        return len(self.frame_list)

    def _get_off_period(self, t_air, dc):
        """Return minimum off-period for duty cycle 1%"""
        return round(t_air * (1.0 / dc - 1))

    #Generate the next time for transmission
    @abstractmethod
    def generate_next_tx_time(self, current_time=0, maximum_time=36000):

        #TODO: Implement correctly this function
        if self.time_mode == "deterministic":
            next_time = current_time + self.interval
        elif self.time_mode == "normal":
            mean = 0.5
            stddev = 0.5 / 3
            next_time = current_time + max(self.interval * np.random.normal(loc=mean, scale=stddev), -1 * current_time)
        elif self.time_mode == "uniform":
            next_time = current_time + max(self.interval * np.random.uniform(low=0, high=1), -1 * current_time)
        elif self.time_mode == 'expo':
            next_time = current_time + random.expovariate(lambd=1./self.interval)
        elif self.time_mode == "naive":
            if current_time == 0:
                # Warm-up period: select uniformly the start time of transmission
                next_time = current_time + np.random.randint(0, self.interval)
            else:
                # Then, deterministic
                next_time = current_time + self.interval
        else:
            raise Exception("Unknown time mode.")

        return round(next_time)

    