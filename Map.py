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
        """Get Map instance

        Raises:
            Exception: Map class has not been instantiated yet.

        Returns:
            Map: Map instance
        """
        if (Map.__instance == None):
            logger.fatal("Map class has not been instantiated!")
            raise Exception("Map class has not been instantiated!")
        
        # Return instance 
        return Map.__instance 

    def __init__(self, size_x=10000, size_y=10000, position_mode="uniform"):
        """Initializes the Map instance

        Args:
            size_x (int, optional): Maximum x size (meters). Defaults to 10000.
            size_y (int, optional): Maximum y size (meters). Defaults to 10000.
            position_mode (str, optional): distribution used to generate positions for devices. Defaults to "uniform".

        Raises:
            Exception: Map class has already been instantiated
        """
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
        """Gets the Map size

        Returns:
            (int, int): x and y size
        """
        return (self.size_x, self.size_y)

    # Return the position mode
    def get_mode(self):
        """Gets position probability distribution

        Returns:
            str: position probability distribution
        """
        return self.position_mode

    # Adds a device to the list of devices
    def add_device(self, device_id, pos):
        """Add devices to the Map

        Args:
            device_id (int): Device id
            pos ((int, int)): Device position (x,y)
        """
        pos_x, pos_y = pos
        
        # Check that device is at a valid position
        if ((pos_x < 0) or (pos_x > self.size_x) or (pos_y < 0) or (pos_y > self.size_y)):
            logger.error("Device={} at wrong position with x={}, y={}.".format(device_id, pos_x, pos_y))

        logger.debug("Adding device={} at position x={}, y={}.".format(device_id, pos_x, pos_y))
        
        # Add device to device list
        self.device_list.append((device_id, (pos_x, pos_y)))

    def add_gateway(self, gw_id, gw_pos):
        """Add gateway to the Map

        Args:
            gw_id (int): Gateway id
            gw_pos ((int, int)): Gateway position (x,y)
        """
        pos_x, pos_y = gw_pos
        self.gateway = ((gw_id,(pos_x, pos_y)))

        logger.debug("Adding gateway={} at position x={}, y={}.".format(gw_id, pos_x, pos_y))
    
    # Returns the device list
    def get_devices(self):
        """Get devices

        Returns:
            [(int, (int, int))]: list of elements (device_id, (pos_x, pos_y))
        """
        return self.device_list

    # Allows to generate a position with normal or uniform distributions
    @staticmethod
    def generate_position():
        """Generate (x,y) position

        Returns:
            (int, int): (x,y) position
        """
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
    def get_distance(pA=None, pB=None):
        # Calculate the distance
        distance = np.sqrt((pB[0] - pA[0])**2 + (pB[1] - pA[1])**2)
        return distance
    
    # Creates a position uniform distribution
    @staticmethod
    def __uniform_distribution():
        """Creates a position uniform distribution

        Returns:
            (float, float): tuple of (x,y) positions between 0 and 1
        """
        x = np.random.uniform(low=0, high=1)
        y = np.random.uniform(low=0, high=1)
        return (x, y)

    # Creates a position normal distribution
    @staticmethod
    def __normal_distribution(): 
        """Creates a position normal distribution

        Returns:
            (float, float): tuple of (x,y) positions.
        """
        mean = 0.5
        stddev = 0.5/3
        x = np.random.normal(loc=mean, scale=stddev)
        y = np.random.normal(loc=mean, scale=stddev)
        return (x, y)
