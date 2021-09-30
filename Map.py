import logging
import numpy as np
logger = logging.getLogger(__name__)

class Map:
    # Singleton, only one instance
    __instance = None

    size_x = 0
    size_y = 0
    size_z = 0
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

    def __init__(self, size_x=10000, size_y=10000, size_z=10000, position_mode="uniform"):
        """Initializes the Map instance

        Args:
            size_x (int, optional): Maximum x size (meters). Defaults to 10000.
            size_y (int, optional): Maximum y size (meters). Defaults to 10000.
            size_z (int, optional): Maximum z size (meters). Defaults to 10000.
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
        Map.size_z = size_z
        Map.position_mode = position_mode

        logger.info("Created simulation map with size x={}, y={}, z={}, with mode={}.".format(self.size_x, self.size_y, self.size_z, self.position_mode))

    # Returns the map size
    def get_size(self):
        """Gets the Map size

        Returns:
            (int, int, int): x, y and z size
        """
        return (self.size_x, self.size_y, self.size_z)

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
            pos (tuple(int, int,int)): Device position (x,y,z)
        """
        pos_x, pos_y, pos_z = pos
        
        # Check that device is at a valid position
        if ((pos_x < 0) or (pos_x > self.size_x) or (pos_y < 0) or (pos_y > self.size_y) or (pos_z < 0) or (pos_z > self.size_z)):
            logger.error("Device={} at wrong position with x={}, y={}, z={}.".format(device_id, pos_x, pos_y, pos_z))

        logger.debug("Adding device={} at position x={}, y={}, z={}.".format(device_id, pos_x, pos_y, pos_z))
        
        # Add device to device list
        self.device_list.append((device_id, (pos_x, pos_y, pos_z)))

    def add_gateway(self, gw_id, gw_pos):
        """Add gateway to the Map

        Args:
            gw_id (int): Gateway id
            gw_pos (tuple(int, int, int)): Gateway position (x,y,z)
        """
        pos_x, pos_y, pos_z = gw_pos
        self.gateway = ((gw_id,(pos_x, pos_y, pos_z)))

        logger.debug("Adding gateway={} at position x={}, y={}, z={}.".format(gw_id, pos_x, pos_y, pos_z))
    
    def get_devices_positions(self):
        """Get devices positions

        Returns:
            [(int, (int, int, int))]: list of elements (device_id, (pos_x, pos_y, pos_z))
        """
        return self.device_list

    def get_gateway_position(self):
        """Get gateway position

        Returns:
            (int, (int, int, int)): tuple of elements (gw_id, (pos_x, pos_y, pos_z))
        """
        return self.gateway


    def generate_position(self):
        """Generate (x,y,z) position

        Returns:
            (tuple(int, int, int)): (x,y,z) position
        """
        # Get the distribution
        if (Map.position_mode == "normal"):
            x, y, z = Map.__normal_distribution()
            # Scale to map
            x = int(x * Map.size_x)
            y = int(y * Map.size_y)
            z = int(z * Map.size_z)
        elif (Map.position_mode == "uniform"):
            x, y, z = Map.__uniform_distribution()
            # Scale to map
            x = int(x * Map.size_x)
            y = int(y * Map.size_y)
            z = int(z * Map.size_z)
        elif (Map.position_mode == "circle"):
            x, y, z = self.__circle_distribution()
        elif (Map.position_mode == "annulus"):
            x, y, z = self.__annulus_distribution()
        else:
            raise("Error!")       
        
        # Ensure minimum values
        x = max(0, x)
        x = min(x, Map.size_x)
        y = max(0, y)
        y = min(y, Map.size_y)
        z = max(0, z)
        z = min(z, Map.size_z)
        
        return (x, y, z)

    # Creates a position uniform distribution
    def __uniform_distribution(self):
        """Creates a position uniform distribution

        Returns:
           pos (tuple(float, float, float)): tuple of (x,y,z) positions between 0 and 1
        """
        x = np.random.uniform(low=0, high=1)
        y = np.random.uniform(low=0, high=1)
        z = np.random.uniform(low=0, high=1)
        return (x, y, z)

    # Creates a position normal distribution
    def __normal_distribution(self): 
        """Creates a position normal distribution

        Returns:
           pos (tuple(float, float, float)): tuple of (x,y,z) positions.
        """
        mean = 0.5
        stddev = 0.5/0.3
        x = np.random.normal(loc=mean, scale=stddev)
        y = np.random.normal(loc=mean, scale=stddev)
        z = np.random.normal(loc=mean, scale=stddev)
        return (x, y, z)

    def __circle_distribution(self):
        noise_std = 5000
        radius = 40000
        alpha = np.random.uniform(0, 2*np.pi)
        noise = np.random.multivariate_normal([0,0], np.array([[noise_std**2, 0], [0, noise_std**2]]))
        x,y = radius*np.array([np.cos(alpha),np.sin(alpha)]).T + np.array([self.gateway[1][0], self.gateway[1][1]]).T + noise.T
        return (x, y, 0)

    def __annulus_distribution(self):
        #radius_min ,radius_max = 3459.24, 27477.7 # +-6 dB
        #radius_min ,radius_max = 1733.73, 54852.2 # +-12 dB
        radius_min ,radius_max = 868.921, 109391 # +-18 dB
        #radius_min ,radius_max = 435.492, 218263 # +-24 dB
        alpha = np.random.uniform(0, 2*np.pi)
        radius = np.random.uniform(radius_min, radius_max)
        x,y = radius*np.array([np.cos(alpha),np.sin(alpha)]).T + np.array([self.gateway[1][0], self.gateway[1][1]]).T
        return (x, y, 0)
    
