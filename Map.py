import logging

logger = logging.getLogger(__name__)

class Map:
    x = 0
    y = 0

    # The Map contains the device list
    device_list = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Adds a device to the list of devices
    def add_device(self, device):
        device_id = device.get_id()
        device_x, device_y = device.get_position()
        logger.info("Adding device={} at position x={}, y={}".format(device_id, device_x, device_y))
        self.device_list.append(device)

    # Adds a list of devices to the list of devices
    def add_devices(self, devices):
        self.device_list.append(devices)
    
    # Returns the device list
    def get_devices(self):
        return self.device_list
    