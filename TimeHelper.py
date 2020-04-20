import numpy as np

class TimeHelper:

    @staticmethod
    def next_time(current_time=None, step_time=None, mode="deterministic"):
        if (mode == "deterministic"):
            next_time = current_time + step_time
        elif (mode == "normal"):
            next_time = current_time + step_time * TimeHelper.__normal_distribution()
        elif (mode == "uniform"):
            next_time = current_time + step_time * TimeHelper.__uniform_distribution()
        else:
            raise("Error!")       
        
        return int(next_time)
    
    @staticmethod
    def __uniform_distribution():
        t = np.random.uniform(low=0, high=1)
        return t

    @staticmethod
    def __normal_distribution(): 
        mean = 0.5
        stddev = 0.5/3
        t = np.random.normal(loc=mean, scale=stddev)
        return t