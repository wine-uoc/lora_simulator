import logging
import math

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

    def set_sf_thresholds(self, area_mode = None, th = None):
        """
        Define the upper thresholds for SF 7 to 12
        """
        assert(area_mode != None)
        
        num_dr = 6 # Number of DRs to divide the area into

        # Equally spaced thresholds assuming map has square form
        if (area_mode == 'distance' and self.sim_map):    
            self.th = tuple(np.linspace(start=0, stop=self.sim_map.size_x, num=num_dr, endpoint=False)[1:])
        
        # Equal area thresholds assuming map has a square form
        elif (area_mode == 'area' and self.sim_map):
            for i in range(1, num_dr + 1):
                # We start at i=1 corresponding to position 0 in the vector
                self.th[i - 1] = self.sim_map.size_x * math.sqrt(i / num_dr)
        
        # Deterministic area thresholds
        elif (area_mode == 'specific' and th != None):
            # th=(10000, 20000, 30000, 40000, 50000, 60000)
            assert (len(th) == 6)
            self.th = th            
        
        # Otherwise, raise error!
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


