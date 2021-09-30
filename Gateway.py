from Map import Map
import logging
import math

import numpy as np

logger = logging.getLogger(__name__)


class Gateway:

    def __init__(self, uid, map_size):
        """Initializes a Gateway instance

        Args:
            uid (int): gateway id
            map_size (int): assuming the map is squared, the side length
        """
        self.id = uid
        self.position = (map_size/2., map_size/2., 0)        

        logger.debug(f'Created gateway={uid} at position x={self.position[0]}, y={self.position[1]}, z={self.position[2]}')

    def set_position(self, size):
        """Sets the position of the gateway in the middle of the map

        Args:
            size (int): side length of the squared map.
        """
        self.position = (size/2., size/2., size/.2)

        logger.info(f"Gateway id:{self.id} placed at {self.position[0]}, {self.position[1]}, {self.position[2]}.")

    def get_id(self):
        return self.id

    def get_position(self):
        return self.position

    def get_auto_dr(self):
        return self.auto_dr

    def calculate_data_rate_and_rx_power(self, target_pos, tx_power, auto_dr):
        """If auto data rate selection is enabled, calculates the appropriate
        DR for the end node and the rx_power of the frames generated by this end node.
        Else, only calculates the rx_power.

        RX power is calculated using the Free-Space Path Loss model.

        Args:
            target_pos (tuple(int, int, int)): (x,y,z) position of the target
            tx_power (int): TX power of target device (dBm)
            auto_dr (bool): Whether LoRa data rate mode selection is automatic or not.

        Returns:
            tuple(int, float): tuple(DR, rx_power)
        """

        # Get distance
        sq_sum = 0
        for i in range(0, len(self.position)):
            sq_sum += (target_pos[i] - self.position[i])**2
        dist = np.sqrt(sq_sum)
        
        # Get Free-Space path loss (in dB)
        # dist (km), freq (GHz)
        if dist == 0:
            FSPL = 0
        else:
            loss_factor = 0 # (dB) it allows to get -137 dBm RX power when gw-to-node dist is 20km (approx. max distance for LoRa)
            FSPL = 20*np.log10(dist/1000.0) + 20*np.log10(868.0/1000.0) + 92.45 + loss_factor
        
        rx_power = tx_power - FSPL # dBm

        if auto_dr:
            # if-else checking sensitivity ranges (from SX1272 datasheet) to set DR properly
            if rx_power >= -124:
                return (5, rx_power) #SF7
            elif -124 > rx_power >= -127:
                return (4, rx_power) #SF8
            elif -127 > rx_power >= -130:
                return (3, rx_power) #SF9
            elif -130 > rx_power >= -133:
                return (2, rx_power) #SF10
            elif -133 > rx_power >= -135:
                return (1, rx_power) #SF11
            else:
                return (0, rx_power) #SF12
        else:
            return (None, rx_power)



