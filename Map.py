import logging
import numpy as np
logger = logging.getLogger(__name__)

class Map:
    # Singleton, only one instance
    __instance = None

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

    def __init__(self, size_x, size_y, size_z, position_mode, position_mode_values):
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
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.position_mode = position_mode
        self.position_mode_values = position_mode_values

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


    def generate_position(self, tx_power):
        """Generate (x,y,z) position

        Args:
            tx_power (int): devices tx_power. Only used for annulus distribution of devices.

        Returns:
            (tuple(int, int, int)): (x,y,z) position
        """
        # Get the distribution
        if (self.position_mode == "normal"):
            x, y, z = self.__normal_distribution()
            # Scale to map
            x = int(x * self.size_x)
            y = int(y * self.size_y)
            z = int(z * self.size_z)
        elif (self.position_mode == "uniform"):
            x, y, z = self.__uniform_distribution()
            # Scale to map
            x = int(x * self.size_x)
            y = int(y * self.size_y)
            z = int(z * self.size_z)
        elif (self.position_mode == "annulus"):
            x, y, z = self.__annulus_distribution(tx_power)
        else:
            raise("Error!")       
        
        # Ensure minimum values
        x = max(0, x)
        x = min(x, self.size_x)
        y = max(0, y)
        y = min(y, self.size_y)
        z = max(0, z)
        z = min(z, self.size_z)
        
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
        stddev = 0.5/self.position_mode_values[0]
        x = np.random.normal(loc=mean, scale=stddev)
        y = np.random.normal(loc=mean, scale=stddev)
        z = np.random.normal(loc=mean, scale=stddev)
        return (x, y, z)


    def __annulus_distribution(self, tx_power):
        
        distance_distr = True

        alpha = np.random.uniform(0, 2*np.pi)

        
        if distance_distr:
            #Uniformly distributed by distance
            radius_min ,radius_max = 6902.08, 13771.5 # +-0 dB
            #radius_min ,radius_max = 3459.24, 27477.7 # +-6 dB
            #radius_min ,radius_max = 1733.73, 54852.2 # +-12 dB
            #radius_min ,radius_max = 868.921, 109391 # +-18 dB
            #radius_min ,radius_max = 435.492, 218263 # +-24 dB

            dist = np.random.uniform(radius_min, radius_max)

        else:
            #Uniformly distributed by power
            #dbm_min, dbm_max = -100, -94 # +- 0dB
            #dbm_min, dbm_max = -106, -88 # +- 6dB
            dbm_min, dbm_max = -112, -82 # +- 12dB
            #dbm_min, dbm_max = -118, -76 # +- 18dB
            #dbm_min, dbm_max = -124, -70 # +- 24dB
            
            dbm = np.random.uniform(dbm_min, dbm_max) 
            dist = np.power(10,((14-dbm-92.45)/20)-np.log10(0.868)+3)

        
        '''
        dist = np.random.uniform(self.position_mode_values[0], self.position_mode_values[1])
        '''
        x,y = dist*np.array([np.cos(alpha),np.sin(alpha)]).T + np.array([self.gateway[1][0], self.gateway[1][1]]).T
        return (x, y, 0)
    
