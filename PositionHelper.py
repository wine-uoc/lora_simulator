import numpy as np

class PositionHelper:

    @staticmethod
    def get_position(mode=None, max_x=None, max_y=None):
        if (mode == "normal"):
            x, y = PositionHelper.__normal_distribution()
        elif (mode == "uniform"):
            x, y = PositionHelper.__uniform_distribution()
        else:
            raise("Error!")       
        
        x = max_x * x
        y = max_y * y
        
        return (x, y)
    
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