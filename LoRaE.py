import logging
from typing import Sequence
from Device import Device
from Sequence import Sequence
from Map import Map
import math

logger = logging.getLogger(__name__)

class LoRaE (Device):

    HOP_SEQ_N_BITS = 9

    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):        
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode)
        (self.__tx_frame_duration_ms,
         self.__tx_header_duration_ms,
         self.__tx_payload_duration_ms
        ) = self.__compute_toa()

        if self.time_mode == 'max':
            self.interval = self.__get_off_period(t_air=self.__tx_frame_duration_ms, dc=0.01)
            self.time_mode = 'expo'

    def create_frame(self):
        pass

    def set_hopping_sequence(self, seq):
        self.hop_seq = seq

    def __compute_toa(self):
        
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

        return hdr_reps * round(t_preamble_ms, t_payload), round(t_preamble_ms), round(t_payload)

        # Performs the scheduled action if required
    def time_step(self, current_time=None, maximum_time=None, sim_grid=None, device_list=None):
        # Check that the current time is the scheduled time of the device
        if (current_time == self.next_time):
            logger.debug("Node id={} executing at time={}.".format(self.dev_id, self.next_time))

            # Create the list of frames to be transmitted depending on LoRa modulation
            frame = self.create_frame(current_time, self.__tx_header_duration_ms + self.__tx_payload_duration_ms)

            # Split frame for frequency hopping
            frames, self.position_hop_list = frame.divide_frame(self.hop_seq,
                                                                self.position_hop_list,
                                                                self.modulation.get_hop_duration(),
                                                                self.__tx_header_duration_ms,
                                                                self.num_rep_header)
            # Append frames to packet list
            self.frame_list.extend(frames)

            # Transmit the list of frames
            Transmission.transmit(frames, sim_grid, device_list)

            # Generate a time for the next transmission when transmission ends
            next_time = self.generate_next_tx_time(current_time = current_time + self.__tx_frame_duration_ms,
                                                        step_time = self.interval,
                                                        mode = self.time_mode)
                                                        
            # If there is time for another action within simulation time, schedule it
            if (next_time + self.__tx_frame_duration_ms < maximum_time):
                self.next_time = next_time
                logger.debug("Node id={} scheduling at time={}.".format(self.dev_id, self.next_time))

