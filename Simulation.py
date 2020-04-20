import logging

import numpy as np

import Map

logger = logging.getLogger(__name__)

class Simulation:
    # Singleton, only one instance
    __instance = None

    simulation_map         = None
    simulation_duration    = 0
    simulation_step        = 0
    simulation_channels    = 0
    simulation_elements    = 0
    simulation_array       = None
    
    @staticmethod
    def get_instance():
        if (Simulation.__instance == None):
            logger.fatal("Simulation class has not been instantiated!")
            raise Exception("Simulation class has not been instantiated!")
        
        # Return instance
        return Simulation.__instance 

    # Class initializer
    # simulation_duration: Time to run the simulation (milliseconds)
    # simulation_step:     Time resolution for the simulation (milliseconds)
    # simulation_map:      Map object that contains the devices to be simulated
    # simulation_channels: Number of channels that the simulation has
    def __init__(self, simulation_duration=1000, simulation_step=1, simulation_channels=1, simulation_map=None):
        assert(simulation_map != None)

        # Check instance exists
        if (Simulation.__instance != None):
            logger.fatal("Simulation class has already been instantiated!")
            raise Exception("Simulation class has already been instantiated!")
        
        # Assign instance
        Simulation.__instance = self

        # Set parameters
        self.simulation_duration = simulation_duration
        self.simulation_step     = simulation_step
        self.simulation_channels = simulation_channels
        self.simulation_map      = simulation_map

        # The simulation elements that have to be performed, where each element represents a millisecond
        self.simulation_elements = int(self.simulation_duration * self.simulation_step)

        # Create a zero-filled matrix with the number of elements and channels
        self.simulation_array = np.zeros((self.simulation_channels, int(self.simulation_elements)))
    
    # Runs the simulation by calling the 'time_step' function of each device
    def run(self):
        # Get the devices in the map
        simulation_devices = self.simulation_map.get_devices()
        
        logger.info("Simulation time duration: {} milliseconds.".format(self.simulation_duration))
        logger.info("Simulation time step: {} milliseconds.".format(self.simulation_step))
        logger.info("Simulation device elements: {} devices.".format(len(simulation_devices)))
        logger.info("Simulation channel elements: {} channels.".format(self.simulation_channels))
        logger.info("Simulation total elements: {}".format(self.simulation_array.shape))
        
        # Initialize the devices in the map
        for device in simulation_devices:
            device.init()

        # Run the simulation for each time step
        for time_step in range(self.simulation_elements):
            # For each time step, execute each device
            for device in simulation_devices:
                device.time_step(current_time=time_step, maximum_time=self.simulation_elements)
