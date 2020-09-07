import logging

import LoraHelper
import Packet
import PositionHelper
import TimeHelper
import Transmission

import numpy as np

logger = logging.getLogger(__name__)


class Device:
    # Class initializer
    # id:            The node unique identifier
    # time_mode:     The distribution of the time error (i.e., normal or uniform)
    # tx_interval:   The period that the node will transmit in seconds (i.e., 60 seconds)
    # tx_rate:       The data rate that the node will transmit in bits/second (i.e., 100 bits/second)
    # tx_payload:    The payload that the node will tranmsit in bytes (i.e., 100 bytes)
    # modulation:    The modulation to use (FHSS or not)
    # hop_duration   The duration in ms of frequency hop
    # hop_list:      The list of sequential frequencies to hop
    def __init__(self, device_id=None, time_mode=None, tx_interval=None, tx_rate=None, tx_payload=None,
                 modulation=None, hop_duration=None, hop_list=None, num_rep_header=None, dr=None, frame_repetitions=1):
        assert (id is not None)

        self.device_id = device_id

        self.time_mode   = time_mode
        self.next_time   = 0
        self.tx_interval = tx_interval
        self.tx_payload  = tx_payload
        self.tx_rate     = tx_rate

        self.dr                = dr
        self.modulation        = modulation
        self.hop_duration      = hop_duration
        self.hop_list          = hop_list
        self.position_hop_list = 0  # current channel to use by the device
        self.num_rep_header    = num_rep_header
        self.frame_repetitions = frame_repetitions
        
        # The list of packets transmitted for frame traceability and metrics computation
        # NOTE: pkt_list[4] does NOT always get pkt number 4, pkt number can be repeated when FHSS split
        self.pkt_list = []

        # Get the time in ms of a packet transmission
        # NOTE: In FHSS, frame time >= header time + pl time, because headers can be repeated 
        self.tx_frame_duration_ms, self.tx_header_duration_ms, self.tx_payload_duration_ms = \
            LoraHelper.LoraHelper.get_time_on_air(self.modulation,
                                                  self.tx_rate,
                                                  self.tx_payload,
                                                  self.dr)

        # Get the minimum tx interval to comply with duty cycle regulations if device wants to transmit at maximum rate
        if self.time_mode == 'max':
            self.tx_interval = LoraHelper.LoraHelper.get_off_period(t_air=self.tx_frame_duration_ms, dc=0.01)
            # Choose transmission mode 
            self.time_mode = 'expo' # sample next time from exponential distribution with lambda = 1/tx_interval

        # Get the x, y position of the device in the map
        self.pos_x, self.pos_y = PositionHelper.PositionHelper.get_position()

        logger.info("Created node with id={} and position x={}, y={}.".format(self.device_id, self.pos_x, self.pos_y))

    # Returns number of packets created
    def get_num_frames(self):
        return len(self.pkt_list)

    # Adds a packet to the node pkt list
    def create_frame(self, current_time, duration, repetition_num):
        frame = Packet.Frame(owner=self.device_id,
                             number=self.get_num_frames(),
                             duration=duration,
                             modulation=self.modulation,
                             start_time=current_time,
                             repetition_number=repetition_num )
        self.pkt_list.append(frame)
        logger.debug("New packet id={}, repetition={}, with duration time={} generated by Node id={} at time={}.".format(frame.number,
                                                                                                         frame.repetition_number,
                                                                                                         frame.duration,
                                                                                                         frame.owner,
                                                                                                         current_time))
        return frame

    # Returns the device id
    def get_id(self):
        return self.device_id

    # Get the node position
    def get_position(self):
        return self.pos_x, self.pos_y

    # Set node position
    def set_position(self, position):
        self.pos_x, self.pos_y = position

    # Returns the time to perform the next action
    def get_next_time(self):
        return self.next_time

    # Initializes the node
    def init(self):
        # Generate a time to start transmitting
        # CAUTION: DOES NOT check if first transmission fits within simulation time (TODO)
        self.next_time = TimeHelper.TimeHelper.next_time(current_time=0,
                                                         step_time=self.tx_interval,
                                                         mode=self.time_mode)
        logger.debug("Node id={} scheduling at time={}.".format(self.device_id, self.next_time))

    # Performs the scheduled action if required
    def time_step(self, current_time=None, maximum_time=None, sim_grid=None, device_list=None):
        # Check that the current time is the scheduled time
        if current_time == self.next_time:
            logger.debug("Node id={} executing at time={}.".format(self.device_id, self.next_time))

            if self.modulation == 'FHSS':
                # Create the list of frames to be transmitted
                frame = self.create_frame(current_time, self.tx_header_duration_ms + self.tx_payload_duration_ms, rep)

                # Frame partition for frequency hopping
                frames, self.position_hop_list = frame.divide_frame(self.hop_list,
                                                                    self.position_hop_list,
                                                                    self.hop_duration,
                                                                    self.tx_header_duration_ms,
                                                                    self.num_rep_header)
                self.pkt_list.pop()
                self.pkt_list.extend(frames)
            else:
                frames = []
                for rep in range(self.frame_repetitions):
                    #for each of the configured repetitions, create the frame
                    frame = self.create_frame(current_time, self.tx_header_duration_ms + self.tx_payload_duration_ms, rep)
                    
                    #set the time for the next repetition -- TODO check the randomization here
                    current_time = current_time + self.tx_header_duration_ms + self.tx_payload_duration_ms + np.random.randint(1, 20)
                    print(current_time)
                                        
                    frames.append(frame)  # must be a list

            # Transmit the list of frames
            Transmission.transmit(frames, sim_grid, device_list)

            # Generate a time for the next transmission when this transmission ends
            next_time = TimeHelper.TimeHelper.next_time(current_time=current_time + self.tx_frame_duration_ms,
                                                        step_time=self.tx_interval,
                                                        mode=self.time_mode)
                                                        
            # If there is time for another action, schedule it
            # i.e., check if next transmission fits within simulation time
            if (next_time + self.tx_frame_duration_ms) < maximum_time:
                self.next_time = next_time
                logger.debug("Node id={} scheduling at time={}.".format(self.device_id, self.next_time))

        # Say something when running
        if self.device_id == 0 and current_time % 60000 == 0:
            print(current_time)
