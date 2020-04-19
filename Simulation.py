import Map

class Simulation:
    map = None
    time = 0
    step = 0
    
    def __init__(self, time=1, step=0.1, map=None):
        assert(map != None)
        self.map = map
    
    def run(self):
        print("Run simulation for {} seconds with {} resolution.".format(self.time, self.step))