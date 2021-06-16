from Device import Device
from Map import Map
import math

class LoRa(Device):
    
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode)
        (self.__tx_frame_duration_ms,
         self.__tx_header_duration_ms,
         self.__tx_payload_duration_ms
        ) = self._compute_toa()

        if self.time_mode == 'max':
            self.interval = self._get_off_period(t_air=self.__tx_frame_duration_ms, dc=0.01)
            self.time_mode = 'expo'

    
    def create_frame(self):
        return 17

    def _compute_toa(self):
        # Convert LORA mode to SF
        if (self.data_rate < 0 or self.data_rate > 5):
            raise Exception("Unknown DR mode.")
        else:
            sf = 12 -  self.data_rate            
        
        # Using default LoRa configuration
        bw = 125            # or 250 [kHz]
        n_preamble = 8      # or 10 preamble length [sym]
        header = True
        cr = 1              # CR in the formula 1 (default) to 4
        crc = True          # CRC for up-link
        IH = not header     # Implicit header
        if (sf == 6): 
            # implicit header only when SF6
            IH = True

        # Low Data Rate Optimization
        DE = (bw == 125 and sf >= 11)

        r_sym = (bw * 1000) / (2 ** sf)
        t_sym = 1. / r_sym * 1000                   # [ms]
        t_preamble = (n_preamble + 4.25) * t_sym    # [ms]

        beta = math.ceil(
            (8 * self.payload_size - 4 * sf + 28 + 16 * crc - 20 * IH) / (4 * (sf - 2 * DE))
        )
        n_payload = 8 + max(beta * (cr + 4), 0)
        t_payload = n_payload * t_sym

        hdr_reps = self.modulation.get_num_hdr_replicas()

        return hdr_reps * round(t_preamble + t_payload), round(t_preamble), round(t_payload)

    def generate_next_tx_time(self, current_time=0, maximum_time=36000):
        next_time = super().generate_next_tx_time(current_time, maximum_time)
        if (next_time + self.__tx_frame_duration_ms < maximum_time):
            self.next_time = next_time