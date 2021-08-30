import logging
from typing import Sequence
from Device import Device
from Sequence import Sequence
from SequenceGenerator import SequenceGenerator
from Map import Map
from Frame import Frame
import math
import numpy as np

logger = logging.getLogger(__name__)

class LoRaE(Device):

    HOP_SEQ_N_BITS = 9

    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode, packet_loss_threshold, position, tx_power, gateway):
        """Initializes LoRaE device

        Args:
            dev_id (int): device id
            data_rate (int): LoRa-E data rate mode
            payload_size (int): payload size
            interval (int): Transmit interval for this device (ms).
            time_mode (str): Time error mode for the transmitting device
            packet_loss_threshold (float): Packet loss threshold.
            position (tuple(float, float,float)): Position of the device in the map.
            tx_power (int): TX power of the device (dBm).
            gateway (Gateway): gateway instance for auto DR selection.
        """      
        super().__init__(dev_id, data_rate, payload_size, interval, time_mode, packet_loss_threshold, position, tx_power, gateway)

        (self.__tx_frame_duration_ms,
         self.__tx_header_duration_ms,
         self.__tx_payload_duration_ms
        ) = self._compute_toa()

        # Current frequency channel to use by the device
        self.num_created_subframes = 0

        if self.time_mode == 'max':
            self.interval = self._get_off_period(t_air=self.__tx_frame_duration_ms, dc=0.01)
            self.time_mode = 'expo'

        self.next_time = None

        self.seq_gen = SequenceGenerator(self.modulation.get_num_subch(), LoRaE.HOP_SEQ_N_BITS,
                                        self.modulation.get_num_usable_freqs())

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
                    dr         = 5, #NOTE: Temporary value to compute frame interferences easily.
                    owner      = owner,
                    number     = number,
                    duration   = duration,
                    start_time = start_time,
                    rx_power   = self.rx_power
                    )

        logger.debug("New packet id={} with duration time={} generated by Node id={} at time={}.".format(number,
                                                                                                         duration,
                                                                                                         owner,
                                                                                                         start_time))
        #Divide Frame into subframes (only for LoRaE devices)
        frames, self.num_created_subframes = frame.divide_frame(
                                                        self.seq_gen,
                                                        self.num_created_subframes,
                                                        self.modulation.get_hop_duration(),
                                                        self.__tx_header_duration_ms,
                                                        self.modulation.get_num_hdr_replicas()
                                                        )
        #save them into self.frame_dict
        if number not in self.frame_dict:
            self.frame_dict[number] = []
            
        self.frame_dict[number].extend(frames)
        
        #return list of frames
        return frames

    def calculate_metrics(self):
        """Calculate metrics.

        Count de-hopped frames and how many of them were collided.

        Returns:
            (int, int): (de_hopped_frames_count, collisions_count)
        """
        de_hopped_frames_count = 0
        collisions_count = 0

        # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided

        for frame_key in self.frame_dict:
            frames_list = self.frame_dict[frame_key]
            #frame_count = len(frames_list)
            #frame_index = 0
            #this_frame = frames_list[0]
    
            # sanity check: first frame in list must be a header
            assert frames_list[0].get_is_header()

            # De-hop the frame to its original form
            total_num_parts = frames_list[0].get_num_parts()
            header_repetitions = frames_list[0].get_num_header_rep()
            headers_to_evaluate = frames_list[:header_repetitions]
            pls_to_evaluate = frames_list[header_repetitions:total_num_parts]

            # At least I need one header not collided
            header_decoded = False
            for header in headers_to_evaluate:
                assert header.get_is_header()         # sanity check
                if not header.get_is_collided():
                    header_decoded = True
                    break

            if header_decoded:
                # Check how many pls collided
                collided_pls_time_count = 0
                non_collided_pls_time_count = 0
                for pl in pls_to_evaluate:
                    assert not pl.get_is_header()     # sanity check 
                    logger.debug(f'FRAME: ({pl.get_owner()},{pl.get_number()},{pl.get_part_num()}) --> Collided intervals: {pl.get_collided_intervals()}')
                    if pl.get_is_collided():
                        # Decide whether a sub-frame is lost or not
                        collided_ratio = pl.get_total_time_colliding() / pl.get_duration()
                        if collided_ratio > self.packet_loss_threshold:
                            # If colided_ratio is greater than packet_loss_threshold,
                            # it is assumed that the entire sub-frame is lost
                            collided_pls_time_count += pl.get_duration()
                        else:
                            # Else, only the collided part is lost
                            collided_pls_time_count += pl.get_total_time_colliding()
                    else:
                        non_collided_pls_time_count += pl.get_duration()

                calculated_ratio = float(
                    non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                # Check for non_collided time ratio.
                if calculated_ratio >= self.modulation.get_numerator_codrate() / 3:
                    # The frame can be retrieved. 
                    de_hopped_frame_collided = False
                else:
                    # The frame is lost.
                    de_hopped_frame_collided = True
            else:
                # As all header replicas are collided, the frame is lost.
                de_hopped_frame_collided = True

            # Prepare next iter
            de_hopped_frames_count = de_hopped_frames_count + 1

            # Increase collision count if frame can not be decoded
            if de_hopped_frame_collided:
                collisions_count = collisions_count + 1
        
        # Sanity check: de-hopped frames should be equal to the number of unique frame ids
        pkt_nums = [int(frame_key) for frame_key in self.frame_dict.keys()]
        assert len(set(pkt_nums)) == de_hopped_frames_count, 'num of de-hopped frames is different than the number of unique frame ids!'

        return (de_hopped_frames_count, collisions_count)

    def set_hopping_sequence(self, seq):
        """Set a hopping sequence for frequency hopping when transmitting

        Args:
            seq [int]: list of tx frequencies
        """
        self.hop_seq = seq

    def get_next_hop_channel(self):
        pass

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
        
        next_time = super().generate_next_tx_time(current_time)
        if (next_time + self.__tx_frame_duration_ms < maximum_time):
            self.next_time = next_time
        else:
            self.next_time = np.inf
        return self.next_time
