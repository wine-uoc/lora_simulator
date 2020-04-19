import numpy as np

class TimeHelper:

    @staticmethod
    def next_time(current_time=None, step_time=None, mode=None):
        next_time = current_time + step_time
        if (mode == "normal"):
            next_time += TimeHelper.__normal_distribution()
        elif (mode == "uniform"):
            next_time += TimeHelper.__uniform_distribution()
        else:
            raise("Error!")       
        
        return next_time
    
    @staticmethod
    def __uniform_distribution():
        x = np.random.uniform(low=0, high=1)
        y = np.random.uniform(low=0, high=1)
        return (x, y)

    @staticmethod
    def __normal_distribution(): 
        mean = 0.5
        stddev = 0.5/3
        x = np.random.normal(loc=mean, scale=stddev)
        y = np.random.normal(loc=mean, scale=stddev)
        return (x, y)