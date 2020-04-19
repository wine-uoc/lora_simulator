import PositionHelper
import TimeHelper

class Device:
    pos_x = 0
    pos_y = 0
    next_time = 0
    tx_interval = 0

    # id:            The node unique identifier
    # position_mode: The distribution of the position error (i.e., normal or uniform)
    # time_mode:     The distribution of the time error (i.e., normal or uniform)
    # max_x:         The maximum x size of the simulation
    # max_y:         The maximum y size of the simulation
    # tx_interval:   The period that the node will transmit in seconds (i.e., 60 seconds)
    # tx_rate:       The data rate that the node will transmit in bits/second (i.e., 100 bits/second)
    # tx_payload:    The payload that the node will tranmsit in bytes (i.e., 100 bytes)
    def __init__(self, device_id=None, time_mode=None, position_mode=None, max_x=None, max_y=None, tx_interval=None, tx_rate=None, tx_payload=None):
        assert(id != None)
        assert(position_mode != None)

        self.device_id = device_id
        
        self.time_mode = time_mode
        self.position_mode = position_mode

        self.next_time = 0
        self.tx_interval = tx_interval
        self.tx_rate     = tx_rate

        # The time in ms that a transmission lasts
        self.tx_duration_ms = 1000 * (self.tx_payload * 8) / self.tx_rate

        # The position of the device in the map
        self.pos_x, self.pos_y = PositionHelper.PositionHelper.get_position(mode=self.position_mode, max_x=self.max_x, max_y=self.max_y)

    def print_position(self):
        print("Node {} at position: x={:.1f} y={:.1f}!".format(self.id, self.pos_x, self.pos_y))

    def get_position(self):
        return (self.pos_x, self.pos_y)
    
    def init(self):
        # Generate a time to start transmitting
        self.next_time = TimeHelper.TimeHelper.next_time(current_time=0, step_time=)

    def run(self, current_time=None, maximum_time=None):
        if (current_time == self.next_time):

            # Generate a time for the next transmission
            next_time = TimeHelper.TimeHelper.next_time(current_time=current_time, step_time=)
            
            # If there is time for another action, schedule it
            if ((next_time + self.tx_duration) < maximum_time):
                self.next_time = next_time
    
