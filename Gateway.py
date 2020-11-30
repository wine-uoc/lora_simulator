import logging
import numpy as np

import PositionHelper

logger = logging.getLogger(__name__)


class Gateway:

    def __init__(self, uid):
        self.id = uid
        self.sim_map = None
        self.x = 0
        self.y = 0

        # Upper thresholds for DR 5-0 or SF 7-12
        self.th = (None, None, None, None, None, None)

    def place_mid(self, sim_map):
        """
        Place the gateway in the middle of the map
        """
        self.sim_map = sim_map

        self.x = self.sim_map.size_x / 2.
        self.y = self.sim_map.size_y / 2.

        logger.info(f"Gateway id:{self.id} placed at {self.x}, {self.y}.")
    
    def get_position(self):
        return self.x, self.y

    def get_sf_thresholds(self):
        return self.th

    def set_sf_thresholds(self, mode, th=None):
        """
        Define the upper thresholds for SF 7 to 12
        """
        if mode == 'equal' and self.sim_map:
            # Equally spaced thresholds assuming map has square form
            self.th = tuple(np.linspace(start=0, stop=self.sim_map.size_x, num=6, endpoint=False)[1:])
        
        elif mode == 'specific' and th:
            # th=(10000, 20000, 30000, 40000, 50000, 60000)
            assert len(th) == 6
            self.th = th            
        
        else:
            raise Exception("Unknown threshold string type or Map")

    def return_data_rate(self, target):
        """
        Return a DR according to distance relative to target
        """
        # Get distance
        dist = PositionHelper.PositionHelper.get_distance(node_a=self, node_b=target) 

        # Compare with thresholds
        for i, th in enumerate(self.th):
            if dist <= th:
                break

        # i = 0 --> closest threshold distance --> SF = 7 --> DR = 5
        if i == len(self.th) - 1:
            dr = len(self.th)
        else:
            dr = len(self.th) - i
            
        return dr


