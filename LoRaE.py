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
                    dr         = 0, #NOTE: Temporary value to compute frame interferences easily. 
                    lost       = self.rx_power < self.modulation.rx_sensitivity[5], # SF7 = DR5
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
                logger.debug(f'Processing LoRa-E (header) frame: ({header.get_owner()},{header.get_number()},{header.get_part_num()})')
                if header.is_lost():
                    #header is lost.
                    logger.debug(f'Frame is LOST!')
                else:
                    # Packet received with enough power.
                    logger.debug(f'Frame is RECEIVED!')
                    if not header.get_is_collided():
                        header_decoded = True
                        logger.debug(f'Frame is NOT collided!')
                        break
                    else:
                        logger.debug(f'Frame is collided!')
                        coll_frames = header.get_collided_frames()
                        hdr_sf = 12 - header.get_data_rate()
                        hdr_time = header.get_duration() / 1000 # in sec
                        hdr_power = (10**(header.get_rx_power()/10)) / 1000 # in W
                        hdr_energy = hdr_time * hdr_power
                        #array to accumulate energy of each interfering frame by SF
                        cumulative_int_energy = np.array([0, 0, 0, 0, 0, 0], dtype=np.float64)
                        #For each frame interfering with header, store its energy

                        visited_frames = [header] # frames already visited (initially only header)
                        to_visit_frames = coll_frames # frames to be visited (initially all frames that collide with header)
                        while len(to_visit_frames) != 0:
                            int_frame = to_visit_frames[0]
                            int_time = header.get_time_colliding_with_frame(int_frame) / 1000 # in sec
                            if int_time != 0:
                                # int_frame actually collides with header. Store its energy according to collision duration.
                                int_frame_sf = 12 - int_frame.get_data_rate()
                                int_frame_power =  (10**(int_frame.get_rx_power() / 10.0)) / 1000 # in W
                                int_frame_energy = int_time * int_frame_power
                                cumulative_int_energy[int_frame_sf - 7] += int_frame_energy
                            to_visit_frames.pop(0)
                            visited_frames.append(int_frame)
                            to_visit_frames.extend([frame for frame in int_frame.get_collided_frames() if frame not in visited_frames])

                        survive = True
                        for currSf in range(7,13):
                            sinr_isolation = self.modulation.sinr[hdr_sf - 7][currSf - 7]
                            if cumulative_int_energy[currSf - 7] != 0:
                                sinr = 10 * np.log10(hdr_energy / cumulative_int_energy[currSf - 7]) # in dB
                            else:
                                sinr = np.inf
                            if sinr >= sinr_isolation:
                                logger.debug(f'Frame survived interference with SF{currSf}')
                            else:
                                survive = False
                                logger.debug(f'Frame destroyed by interference with SF{currSf}')
                                break
                        if survive:
                            header_decoded = True
                            break

            if header_decoded:
                # Check how many pls collided
                collided_pls_time_count = 0
                non_collided_pls_time_count = 0
                for pl in pls_to_evaluate:
                    assert not pl.get_is_header()     # sanity check 
                    logger.debug(f'Processing LoRa-E (payload) subframe: ({pl.get_owner()},{pl.get_number()},{pl.get_part_num()})')
                    pl_sf = 12 - pl.get_data_rate()
                    if pl.is_lost():
                        #Payload frame received with too small power. Consider it lost.
                        logger.debug(f'Subframe is LOST!')
                        collided_pls_time_count += pl.get_duration()
                    else:
                        #Payload frame received with enough power.
                        logger.debug(f'Subframe is RECEIVED!')
                        if not pl.get_is_collided():
                            logger.debug(f'Subframe is NOT collided!')
                            # Payload frame is not collided with any other frame(s).
                            non_collided_pls_time_count += pl.get_duration()
                        else:
                            logger.debug(f'Subframe is collided!')
                            # Payload frame collides with some other frame(s)
                            coll_frames = pl.get_collided_frames()
                            pl_time = pl.get_duration() / 1000 # in sec
                            pl_power = (10**(pl.get_rx_power()/10)) / 1000 # in W
                            pl_energy = pl_time * pl_power
                            cumulative_int_energy = [[0.0, []] for _ in range(0,6)]
                            
                            visited_frames = [pl] # frames already visited (initially only pl)
                            to_visit_frames = coll_frames # frames to be visited (initially all frames that collide with pl)
                            while len(to_visit_frames) != 0:
                                int_frame = to_visit_frames[0]
                                int_time = pl.get_time_colliding_with_frame(int_frame) / 1000 # in sec
                                if int_time != 0:
                                    # int_frame actually collides with pl. Store its energy according to collision duration.
                                    int_frame_sf = 12 - int_frame.get_data_rate()
                                    int_frame_power =  (10**(int_frame.get_rx_power() / 10.0)) / 1000 # in W
                                    int_frame_energy = int_time * int_frame_power
                                    cumulative_int_energy[int_frame_sf - 7][0] += int_frame_energy
                                    cumulative_int_energy[int_frame_sf - 7][1].append(int_frame)
                                to_visit_frames.pop(0) # int_frame already visited
                                visited_frames.append(int_frame) # add int_frame into visited_frames list
                                to_visit_frames.extend([frame for frame in int_frame.get_collided_frames() if frame not in visited_frames]) #

                            # Store SFs that destroy pkt. It allows us to find out how much bits of pkt are corrupted.
                            destructive_sf = []
                            for currSf in range(7,13):
                                sinr_isolation = self.modulation.sinr[pl_sf - 7][currSf - 7]
                        
                                if cumulative_int_energy[currSf - 7][0] != 0:
                                    sinr = 10 * np.log10(pl_energy / cumulative_int_energy[currSf - 7][0]) # in dB
                                else:
                                    sinr = np.inf

                                if sinr >= sinr_isolation:
                                    logger.debug(f'Subframe survived interference with SF{currSf}')
                                else:
                                    destructive_sf.append(currSf)
                                    logger.debug(f'Subframe destroyed by interference with SF{currSf}')
                        
                            #Calculate the amount of time pl is actually colliding.
                            actual_coll_frames = []
                            for sf in destructive_sf:
                                actual_coll_frames += cumulative_int_energy[sf - 7][1]

                            actual_coll_time = pl.get_time_colliding_with_frames(actual_coll_frames)
                            assert actual_coll_time <= pl.get_duration() # sanity check
                            pl_subf_collided_ratio = actual_coll_time / pl.get_duration()

                            if pl_subf_collided_ratio > self.packet_loss_threshold:
                                # If colided_ratio is greater than packet_loss_threshold,
                                # it is assumed that the entire sub-frame is lost
                                collided_pls_time_count += pl.get_duration()
                            else:
                                # Else, only the collided part is lost
                                collided_pls_time_count += actual_coll_time
                                non_collided_pls_time_count += (pl.get_duration() - actual_coll_time)

                full_payload_collided_ratio = float(
                    non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                
                if full_payload_collided_ratio >= self.modulation.get_numerator_codrate() / 3:
                    # Frame can be retrieved. 
                    de_hopped_frame_collided = False
                else:
                    # Frame is lost.
                    de_hopped_frame_collided = True
            else:
                # Since all header replicas are collided, the frame is lost.
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
