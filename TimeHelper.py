import numpy as np


class TimeHelper:

    # Generates a time with deterministic, normal or uniform distributions
    @staticmethod
    def next_time(current_time=None, step_time=None, mode="deterministic", tx_duration=None):
        if mode == "deterministic":
            next_time = current_time + step_time
        elif mode == "normal":
            next_time = current_time + step_time + abs(TimeHelper.__normal_distribution())
        elif mode == "uniform":
            next_time = current_time + step_time + TimeHelper.__uniform_distribution()
        else:
            raise Exception("Error!")

        # next_time must be greater than current_time+tx_duration, ie do not transmit if device is transmitting
        if current_time:    # except for first transmission
            assert next_time > current_time + tx_duration

        return int(next_time)
    
    # Creates a time uniform distribution
    @staticmethod
    def __uniform_distribution():
        t = np.random.randint(low=0, high=1000)
        return t

    # Creates a time normal distribution
    @staticmethod
    def __normal_distribution(): 
        mean = 0.       # set as summation to respect somehow in average the device_tx_interval set in configuration
        stddev = 1000   # recall 1 is 1 ms, so 65% will fall within 1000 milliseconds
        t = np.random.normal(loc=mean, scale=stddev)
        return t
