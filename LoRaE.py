from Device import Device
import math

class LoRaE (Device):

    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode)

    def createFrame(self):
        pass

    def __compute_toa(self):
        
        t_preamble_ms = 233

        # # OLD calculation apporach
        # t_payload = 1000 * (pl_bytes * 8 + 16) / dr_bps  # [ms] + 16 bc payload CRC is 2B
        # t_preamble = 1000 * 114 / dr_bps  # [ms] 114 = sync-word + (preamble + header) * CR2/1 + 2b
        bitrate = self.modulation.get_bitrate()
        payload = self
        if bitrate == 162:
            t_payload = math.ceil((pl_bytes + 2) / 2) * 102
        elif bitrate == 325:
            t_payload = math.ceil((pl_bytes + 2) / 4) * 102
        else:
            raise Exception("Unknown bitrate.")

        return (t_preamble_ms, t_payload)