import logging

import numpy
from Device import Device
from Map import Map
from Frame import Frame

import math

logger = logging.getLogger(__name__)

class LoRa(Device):
    
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode, packet_loss_threshold, gateway=None):
        """Initializes LoRa device

        Args:
            dev_id (int): device id
            data_rate (int): LoRa data rate mode
            payload_size (int): payload size
            interval (int): Transmit interval for this device (ms).
            time_mode (str): Time error mode for the transmitting device
            packet_loss_threshold (float): Packet loss threshold.
            gateway (Gateway): gateway instance for auto DR selection. Defaults to None.
        """
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode, packet_loss_threshold, gateway)
        (self.__tx_frame_duration_ms,
         self.__tx_header_duration_ms,
         self.__tx_payload_duration_ms
        ) = self._compute_toa()

        if self.time_mode == 'max':
            self.interval = self._get_off_period(t_air=self.__tx_frame_duration_ms, dc=0.01)
            self.time_mode = 'expo'

        self.next_time = None
    
    def create_frame(self):
        #Create Frame
        """Creates a Frame to be transmitted

        Returns:
            [Frame]: frame instance in a list
        """
        owner = self.dev_id
        number = self.get_frame_dict_length()
        duration = self.__tx_header_duration_ms + self.__tx_payload_duration_ms
        start_time = self.next_time
        frame = Frame(
                    owner      = self.dev_id,
                    number     = self.get_frame_dict_length(),
                    duration   = self.__tx_header_duration_ms + 
                                 self.__tx_payload_duration_ms,
                    start_time = self.next_time
                    )

        logger.debug("New packet id={} with duration time={} generated by Node id={} at time={}.".format(number,
                                                                                                         duration,
                                                                                                         owner,
                                                                                                         start_time))
    
        #save them into self.frame_dict
        if number not in self.frame_dict:
            self.frame_dict[number] = []
            
        self.frame_dict[number].append(frame)

        #return created frame
        return [frame]

    def calculate_metrics(self):
        """Calculate metrics.

        Count frames and how many of them were collided.

        Returns:
            (int, int): (frames_count, collisions_count)
        """
        frames = self.frame_dict.values()
        frames_list = sum(frames, [])
        # how many of them collided
        count = 0
        for pkt in frames_list:
            #lora_num_collisions_per_pkt_coll.append(len(pkt.get_collided_intervals()))
            if pkt.get_is_collided():
                collided_ratio = pkt.get_total_time_colliding() / pkt.get_duration()
                if collided_ratio > self.packet_loss_threshold:
                    count += 1
            logger.debug(f'FRAME: ({pkt.get_owner()},{pkt.get_number()},{pkt.get_part_num()}) --> Collided intervals: {pkt.get_collided_intervals()}')
        
        return (len(self.frame_dict), count)

    def get_next_tx_time(self):
        """Gets next tx time

        Returns:
            int: next tx time
        """
        return self.next_time

    def _compute_toa(self):
        """Computes time on air LoRa devices transmissions

        Raises:
            Exception: Unknown data rate mode

        Returns:
            (int, int, int): (tx_frame_duration, tx_header_duration, tx_payload_duration) in ms
        """
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

    def generate_next_tx_time(self, current_time, maximum_time):
        """Generates the next tx time

        Args:
            current_time (int): lower bound instant of time
            maximum_time (int): upper bound instant of time

        Returns:
            int: instant of time between current_time and maximum_time
        """
        next_time = super().generate_next_tx_time(current_time)
        if (next_time + self.__tx_frame_duration_ms < maximum_time):
            self.next_time = next_time
        else:
            self.next_time = numpy.inf
            
        return self.next_time