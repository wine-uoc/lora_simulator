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
        
        # Scale to map
        x = int(x * x_max)
        y = int(y * y_max)

        # Ensure minimum values
        x = max(0, x)
        x = min(x, x_max)
        y = max(0, y)
        y = min(y, y_max)
        
        return (x, y)
    
    # Calculates the distance between two nodes
    @staticmethod
    def get_distance(node_a=None, node_b=None):
        # Get node A and B positions
        pA = node_a.get_position()
        pB = node_b.get_position()

        # Calculate the distance
        distance = np.sqrt((pB[0] - pA[0])**2 + (pB[1] - pA[1])**2)
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