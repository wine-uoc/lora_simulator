import logging
from typing import Sequence
from Device import Device
from Sequence import Sequence
from Map import Map
from Frame import Frame
import math

logger = logging.getLogger(__name__)

class LoRaE(Device):

    HOP_SEQ_N_BITS = 9

    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        """Initializes LoRaE device

        Args:
            dev_id (int): device id
            data_rate (int): LoRa-E data rate mode
            payload_size (int): payload size
            interval (int): Transmit interval for this device (ms).
            time_mode (str): Time error mode for the transmitting device
        """      
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode)

        (self.__tx_frame_duration_ms,
         self.__tx_header_duration_ms,
         self.__tx_payload_duration_ms
        ) = self._compute_toa()

        # Current frequency channel to use by the device
        self.position_hop_seq = 0

        if self.time_mode == 'max':
            self.interval = self._get_off_period(t_air=self.__tx_frame_duration_ms, dc=0.01)
            self.time_mode = 'expo'

        self.next_time = None

    def create_frame(self):
        """Creates a Frame and divides it into sub-Frames.

        Returns:
           [Frame]: list of frame instances
        """
    
        owner = self.dev_id
        number = self.get_frame_dict_length()
        duration = self.__tx_header_duration_ms + self.__tx_payload_duration_ms
        start_time = self.next_time
        frame = Frame(
                    owner      = owner,
                    number     = number,
                    duration   = duration,
                    start_time = start_time
                    )

        logger.debug("New packet id={} with duration time={} generated by Node id={} at time={}.".format(number,
                                                                                                         duration,
                                                                                                         owner,
                                                                                                         start_time))
        #Divide Frame into subframes (only for LoRaE devices)
        frames, self.position_hop_seq = frame.divide_frame(
                                                        self.hop_seq,
                                                        self.position_hop_seq,
                                                        self.modulation.get_hop_duration(),
                                                        self.__tx_header_duration_ms,
                                                        self.modulation.get_num_hdr_replicas()
                                                        )
        #save them into self.frame_list
        if number not in self.frame_list:
            self.frame_list[number] = []
            
        self.frame_list[number].extend(frames)
        

        
        #return list of frames
        return frames

    def set_hopping_sequence(self, seq):
        """Set a hopping sequence for frequency hopping when transmitting

        Args:
            seq [int]: list of tx frequencies
        """
        self.hop_seq = seq

    def get_next_tx_time(self):
        """Gets next tx time

        Returns:
            int: next tx time
        """
        return self.next_time

    def _compute_toa(self):
        """Computes time on air for LoRa-E devices transmissions

        Raises:
            Exception: Unknown data rate mode

        Returns:
            (int, int, int): (tx_frame_duration, tx_header_duration, tx_payload_duration) in ms
        """
        
        t_preamble_ms = 233

        # # OLD calculation apporach
        # t_payload = 1000 * (pl_bytes * 8 + 16) / dr_bps  # [ms] + 16 bc payload CRC is 2B
        # t_preamble = 1000 * 114 / dr_bps  # [ms] 114 = sync-word + (preamble + header) * CR2/1 + 2b
        bitrate = self.modulation.get_bitrate()
        if bitrate == 162:
            t_payload = math.ceil((self.payload_size + 2) / 2) * 102
        elif bitrate == 325:
            t_payload = math.ceil((self.payload_size + 2) / 4) * 102
        else:
            raise Exception("Unknown bitrate.")

        hdr_reps = self.modulation.get_num_hdr_replicas()

        return hdr_reps * round(t_preamble_ms + t_payload), round(t_preamble_ms), round(t_payload)

        
    def generate_next_tx_time(self, current_time, maximum_time):
        """Generates the next tx time

        Args:
            current_time (int): lower bound instant of time
            maximum_time (int): upper bound instant of time

        Returns:
            int: instant of time between current_time and maximum_time
        """
        
        next_time = super().generate_next_tx_time(current_time, maximum_time)
        if (next_time + self.__tx_frame_duration_ms < maximum_time):
            self.next_time = next_time
        else:
            self.next_time = None
        return self.next_time
