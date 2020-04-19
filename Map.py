class Map:
    x = 0
    y = 0

    device_list = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def add_device(self, device):
        self.device_list.append(device)

    def add_devices(self, devices):
        self.device_list.append(devices)
    
    def get_devices(self):
        return self.device_list
    