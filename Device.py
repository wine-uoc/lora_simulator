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
        """Initializes a Device

        Args:
            dev_id (int): device id
            data_rate (int): LoRa-E data rate mode
            payload_size (int): payload size
            interval (int): Transmit interval for this device (ms).
            time_mode (str): Time error mode for the transmitting device
        """      
        super().__init__()
        self.modulation = Modulation(data_rate)
        self.dev_id = dev_id
        self.data_rate = data_rate
        self.payload_size = payload_size
        self.interval = interval
        self.time_mode = time_mode

        # The list of frames transmitted for frame traceability and metrics computation
        self.frame_list = dict()

        self._generate_position()

    @abstractmethod
    def create_frame(self):
        """Creates a Frame. Implemented in subclasses.
        """
        pass

    @abstractmethod
    def _compute_toa(self):
        """Computes time on air of the packets. Implemented in subclasses.
        """
        pass

    def _generate_position(self):
        """Generates a position for the device in a 2D Map
        """
        self.position = Map.get_position()

    def get_modulation_data (self):
        """Gets modulation data of the device

        Returns:
            dict: dictionary with modulation data of the device
        """
        return self.modulation.get_data()

    def get_dev_id(self):
        """Gets the device id

        Returns:
            int: device id
        """
        return self.dev_id

    def get_data_rate(self):
        """Gets the data rate of the device

        Returns:
            int: data rate
        """
        return self.data_rate

    def get_payload_size(self):
        """Gets the payload size.

        Returns:
            int: payload size (bytes)
        """
        return self.payload_size

    def get_interval(self):
        """Gets the transmit interval for this device

        Returns:
            int: transmit interval (ms)
        """
        return self.interval

    def get_time_mode(self):
        """Gets the time error mode for this device.

        Returns:
            str: time mode
        """
        return self.time_mode

    def get_position(self):
        """Gets the position of the device in a 2D Map

        Returns:
            (int, int): tuple with (x,y) position
        """
        return self.position

    def get_frame_dict(self):
        """Gets frame list

        Returns:
            [Frame]: list of frames the device has created
        """
        return self.frame_list

    def get_frame_dict_length(self):
        """Gets the frame list length for the device

        Returns:
            int: frame list length
        """
        return len(self.frame_list)

    def _get_off_period(self, t_air, dc=0.01):
        """computes the minimum off-period for duty cycle dc. Actually dc=0.01

        Args:
            t_air (int): amount of time transmitting a frame
            dc (optional, float): duty cycle

        Returns:
            int: time interval within which the device is not allowed to transmit frames.
        """
        return round(t_air * (1.0 / dc - 1))

    #Generate the next time for transmission
    @abstractmethod
    def generate_next_tx_time(self, current_time, maximum_time):
        """Generates the next tx time

        Args:
            current_time (int): lower bound instant of time
            maximum_time (int): upper bound instant of time

        Returns:
            int: instant of time between current_time and maximum_time
        """

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

    