import numpy as np

import Map

class PositionHelper:

    # Allows to generate a position with normal or uniform distributions
    @staticmethod
    def get_position():
        # Get Map instance
        map = Map.Map.get_instance()

        # Get Map size and mode
        x_max, y_max = map.get_size()
        mode         = map.get_mode()

        # Get the distrbution
        if (mode == "normal"):
            x, y = PositionHelper.__normal_distribution()
        elif (mode == "uniform"):
            x, y = PositionHelper.__uniform_distribution()
        else:
            raise("Error!")       
        
        # Scale to the map size
        x = int(x_max * x)
        y = int(y_max * y)
        
        return (x, y)
    
    # Calculates the distance between two nodes
    @staticmethod
    def get_distance(device_a=None, device_b = None):
        distance = 0
        
        # Get device A and B positions
        device_a_x, device_a_y = device_a.get_position()
        device_b_x, device_b_y = device_b.get_position()
        
        # Calculate the distance
        # TODO
        
        return distance
    
    # Creates a position uniform distribution
    @staticmethod
    def __uniform_distribution():
        x = np.random.uniform(low=0, high=1)
        y = np.random.uniform(low=0, high=1)
        return (x, y)

    # Creates a position normal distribution
    @staticmethod
    def __normal_distribution(): 
        mean = 0.5
        stddev = 0.5/3
        x = np.random.normal(loc=mean, scale=stddev)
        y = np.random.normal(loc=mean, scale=stddev)
        return (x, y)