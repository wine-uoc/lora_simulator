from Map import Map
import logging
import math

import numpy as np

logger = logging.getLogger(__name__)


class Gateway:

    def __init__(self, uid, map_size, area_mode, th=None):
        """Initializes a Gateway instance

        Args:
            uid (int): gateway id
            map_size (int): assuming the map is squared, the side length
            area_mode (str): Area mode to assign DR (i.e., circles with equal distance or circles with equal area)
            th ((int,int,int,int,int,int), optional): Preset thresholds. Defaults to None.
        """
        self.id = uid
        self.position = (map_size/2., map_size/2.)
        
        # Upper thresholds for DR 5-0 or SF 7-12
        self.th = (None, None, None, None, None, None)
        self.__generate_SF_thresholds(map_size, area_mode, th)

    def set_position(self, size):
        """Sets the position of the gateway in the middle of the map

        Args:
            size (int): side length of the squared map.
        """
        self.position = (size/2., size/2.)

        logger.info(f"Gateway id:{self.id} placed at {self.position[0]}, {self.position[1]}.")

    def get_id(self):
        return self.id

    def get_position(self):
        return self.position

    def get_SF_thresholds(self):
        return self.th

    def __generate_SF_thresholds(self, map_size, area_mode = None, th=None):
        """
        Define the upper thresholds for SF 7 to 12
        """
        assert(area_mode != None)
        
        num_dr = 6 # Number of DRs to divide the area into

        # Equally spaced thresholds assuming map has square form
        if (area_mode == 'distance'):    
            self.th = tuple(np.linspace(start=0, stop=map_size, num=num_dr, endpoint=False)[1:])
        
        # Equal area thresholds assuming map has a square form
        elif (area_mode == 'area'):
            for i in range(1, num_dr + 1):
                # We start at i=1 corresponding to position 0 in the vector
                self.th[i - 1] = map_size * math.sqrt(i / num_dr)
        
        # Deterministic area thresholds
        elif (area_mode == 'specific' and th != None):
            # th=(10000, 20000, 30000, 40000, 50000, 60000)
            assert (len(th) == 6)
            self.th = th            
        
        # Otherwise, raise error!
        else:
            raise Exception("Unknown threshold string type or Map")

    def get_data_rate(self, target_pos):
        """
        Return a DR according to distance relative to target
        """
        # Get distance
        dist = Map.get_distance(pA=self.position, pB=target_pos) 

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


