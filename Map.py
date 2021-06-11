import logging
import numpy as np
logger = logging.getLogger(__name__)

class Map:
    # Singleton, only one instance
    __instance = None

    size_x = 0
    size_y = 0
    position_mode = None

    # The Map class contains the device list
    device_list = []

    @staticmethod
    def get_instance():
        if (Map.__instance == None):
            logger.fatal("Map class has not been instantiated!")
            raise Exception("Map class has not been instantiated!")
        
        # Return instance 
        return Map.__instance 

    # Class initializer
    # size_x: Maximum x size (millimiters, default = 10 meters)
    # size_y: Maximum y size (millimiters, default = 10 meters)
    def __init__(self, size_x=10000, size_y=10000, position_mode="uniform"):
        # Check instance exists
        if (Map.__instance != None):
            logger.fatal("Map class has already been instantiated!")
            raise Exception("Map class has already been instantiated!")
        
        # Assign instance
        Map.__instance = self

        # Assign other parameters
        Map.size_x = size_x
        Map.size_y = size_y
        Map.position_mode = position_mode

        logger.info("Created simulation map with size x={}, y={} with mode={}.".format(self.size_x, self.size_y, self.position_mode))

    # Returns the map size
    def get_size(self):
        return (self.size_x, self.size_y)

    # Return the position mode
    def get_mode(self):
        return self.position_mode

    # Adds a device to the list of devices
    def add_device(self, device):
        # Get device identifier and position
        device_id = device.get_id()
        device_x, device_y = device.get_position()
        
        # Check that device is at a valid position
        if ((device_x < 0) or (device_x > self.size_x) or (device_y < 0) or (device_y > self.size_y)):
            logger.error("Device={} at wrong position with x={}, y={}.".format(device_id, device_x, device_y))

        logger.debug("Adding device={} at position x={}, y={}.".format(device_id, device_x, device_y))
        
        # Add device to device list
        self.device_list.append(device)
    
    # Returns the device list
    def get_devices(self):
        return self.device_list

    # Allows to generate a position with normal or uniform distributions
    @staticmethod
    def get_position():

        # Get the distribution
        if (Map.position_mode == "normal"):
            x, y = Map.__normal_distribution()
        elif (Map.position_mode == "uniform"):
            x, y = Map.__uniform_distribution()
        else:
            raise("Error!")       
        
        # Scale to map
        x = int(x * Map.size_x)
        y = int(y * Map.size_y)

        # Ensure minimum values
        x = max(0, x)
        x = min(x, Map.size_x)
        y = max(0, y)
        y = min(y, Map.size_y)
        
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
