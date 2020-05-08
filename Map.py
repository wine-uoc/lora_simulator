import logging

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
        self.size_x = size_x
        self.size_y = size_y
        self.position_mode = position_mode

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
