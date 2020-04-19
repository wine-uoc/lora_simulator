import Map

class Simulation:
    map = None
    simulation_duration = 0
    simulation_step = 0
    simulation_items = 0

    # time: Time to run the simulation (seconds)
    # step: Time resolution for the simulations (seconds)
    # map: Map object that contains the devices
    def __init__(self, simulation_duration=1, simulation_step=0.001, map=None):
        assert(map != None)
        self.simulation_duration = simulation_duration
        self.simulation_step = simulation_step
        self.simulation_items = self.simulation_duration / self.simulation_step
        self.map = map
    
    def run(self):
        pass