import logging

logger = logging.getLogger(__name__)

class Map:
    x = 0
    y = 0

    # The Map class contains the device list
    device_list = []

    # Class initializer
    # x: Maximum x size (millimiters)
    # y: Maximum y size (millimiters)
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Adds a device to the list of devices
    def add_device(self, device):
        # Get device identifier and position
        device_id = device.get_id()
        device_x, device_y = device.get_position()
        
        # Check that device is at a valid position
        if (device_x < 0 or device_x > self.x or device_y < 0 or device_y > self.y):
            logger.error("Device={} at wrong position with x={}, y={}.")

        logger.info("Adding device={} at position x={}, y={}.".format(device_id, device_x, device_y))
        
        # Add device to device list
        self.device_list.append(device)
    
    # Returns the device list
    def get_devices(self):
        return self.device_list
    