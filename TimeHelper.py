import numpy as np


class TimeHelper:

    # Generates a time with deterministic, normal or uniform distributions
    @staticmethod
    def next_time(current_time=None, step_time=None, mode="deterministic"):
        if mode == "deterministic":
            next_time = current_time + step_time
        elif mode == "normal":
            next_time = current_time + max(step_time * TimeHelper.__normal_distribution(), -current_time)
        elif mode == "uniform":
            next_time = current_time + max(step_time * TimeHelper.__uniform_distribution(), -current_time)
        elif mode == "max-duty":
            if current_time == 0:
                # Warm-up period: select uniformly the start time of transmission
                next_time = current_time + np.random.randint(0, step_time)
            else:
                next_time = current_time + step_time
        else:
            raise Exception("Unknown time mode.")

        return int(next_time)

    # Creates a time uniform distribution
    @staticmethod
    def __uniform_distribution():
        t = np.random.uniform(low=0, high=1)
        return t
        # Creates a time normal distribution

    @staticmethod
    def __normal_distribution():
        mean = 0.5
        stddev = 0.5 / 3
        t = np.random.normal(loc=mean, scale=stddev)
        return t
