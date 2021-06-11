from Device import Device

class LoRa(Device):
    
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode)
        


    def createFrame(self):
        pass

    def __compute_toa(self):
