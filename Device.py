from abc import ABC, abstractmethod
from Map import Map
from Modulation import Modulation

class Device(ABC):

    @abstractmethod
    def __init__(self, dev_id, data_rate, payload_size, interval, time_mode):
        super().__init__()
        self.modulation = Modulation(data_rate)
        self.dev_id = dev_id
        self.data_rate = data_rate
        self.payload_size = payload_size
        self.time_mode = time_mode

    @abstractmethod
    def createFrame(self):
        pass

    def generatePosition(self):
        self.position = Map.get_position()

    def get_modulation_data (self):
        return self.modulation.get_data()

    def get_off_period(t_air, dc):
        """Return minimum off-period for duty cycle 1%"""
        return round(t_air * (1.0 / dc - 1))

    #Generate the next time for transmission
    def next_time(self):
        #TODO: Implement correctly this function
        if self.time_mode == "deterministic":
            next_time = current_time + step_time
        elif self.time_mode == "normal":
            next_time = current_time + max(step_time * TimeHelper.__normal_distribution(), -1 * current_time)
        elif self.time_mode == "uniform":
            next_time = current_time + max(step_time * TimeHelper.__uniform_distribution(), -1 * current_time)
        elif self.time_mode == 'expo':
            next_time = current_time + TimeHelper.__exponential(1./step_time)
        elif self.time_mode == "naive":
            if current_time == 0:
                # Warm-up period: select uniformly the start time of transmission
                next_time = current_time + np.random.randint(0, step_time)
            else:
                # Then, deterministic
                next_time = current_time + step_time
        else:
            raise Exception("Unknown time mode.")

        return round(next_time)