from Map import Map
from Device import Device
import logging
from LoRa import LoRa

import numpy as np

logger = logging.getLogger(__name__)


class Simulation:
    # Singleton, only one instance
    __instance = None

    simulation_map = None
    simulation_duration = 0
    simulation_step = 0
    simulation_channels = 0
    simulation_elements = 0
    simulation_grid = None

    @staticmethod
    def get_instance():
        if Simulation.__instance is None:
            logger.fatal("Simulation class has not been instantiated!")
            raise Exception("Simulation class has not been instantiated!")

        # Return instance
        return Simulation.__instance

    # Class initializer
    # simulation_duration: Time to run the simulation (milliseconds)
    # simulation_step:     Time resolution for the simulation (milliseconds)
    # simulation_map:      Map object that contains the devices to be simulated
    # simulation_channels: Number of channels that the simulation has
    
    def __init__(
        self, size, devices,
        time, step, interval,
        number_runs, position_mode, time_mode,
        area_mode, payload_size, percentage,
        data_rate_lora, data_rate_lora_e
    ): 
        """Initializes Simulation instance

        Args:
            size (int): Size of each simulation area side (i.e., x and y) in millimiters.
            devices (int): Number of total devices in the simulation.
            time (int): Duration of the simulation in milliseconds.
            step (int): Time step of the simulation in milliseconds.
            interval (int): Transmit interval for each device (ms).
            number_runs (int): Number of script runs.
            position_mode (str): Node positioning mode (i.e., normal distribution or uniform distribution).
            time_mode (str): Time error mode for transmitting devices (i.e., normal, uniform or exponential distribution).
            area_mode (str): Area mode to assign DR (i.e., circles with equal distance or circles with equal area).
            payload_size (int): Transmit payload of each device (bytes).
            percentage (int): Percentage of LoRa devices with respect to LoRa-E (i.e., 1.0 is all LoRa devices).
            data_rate_lora (int): LoRa data rate mode.
            data_rate_lora_e (int): LoRa-E data rate mode.

        Raises:
            Exception: [description]
        """
    
        # Check instance exists
        if Simulation.__instance is not None:
            logger.fatal("Simulation class has already been instantiated!")
            raise Exception("Simulation class has already been instantiated!")

        # Assign instance
        Simulation.__instance = self

        
        num_devices_lora = int(devices*percentage)
        num_devices_lora_e = devices - num_devices_lora

        # Initialize LoRa and LoRa-E Devices
        self.devices = []
        for dev_id in range (num_devices_lora):
            lora_device = LoRa(
                            dev_id, data_rate_lora, payload_size,
                            interval, time_mode
                        )
        self.map = Map(size, size, position_mode)
        # Set parameters
        self.simulation_duration = time
        self.simulation_step = step
        self.simulation_channels = simulation_channels #it depends on the chosen Lora-E DR
        self.simulation_map = simulation_map

        # The simulation elements that have to be performed, where each element represents a millisecond
        self.simulation_elements = int(
            self.simulation_duration * self.simulation_step)

        # Create a zero-filled matrix with the number of elements and channels
        # TODO: initiallize array with custom type of tuple(int32, int32, int32) corresponding to (frame.owner, frame.number, frame.part_num)
        self.simulation_grid = np.zeros(
            (self.simulation_channels, int(self.simulation_elements)), dtype=(np.int32, 3))

    # Runs the simulation by calling the 'time_step' function of each device
    def run(self):
        # Get the devices in the map
        simulation_devices = self.simulation_map.get_devices()

        logger.info(
            f"Simulation time duration: {self.simulation_duration} milliseconds.")
        logger.info(
            f"Simulation time step: {self.simulation_step} milliseconds.")
        logger.info(
            f"Simulation device elements: {len(simulation_devices)} devices.")
        logger.info(
            f"Simulation channel elements: {self.simulation_channels} channels.")
        logger.info(
            f"Simulation total elements: {self.simulation_grid.shape}.")

        # Initialize the devices in the map
        for device in simulation_devices:
            device.init()

        # Run the simulation for each time step
        for time_step in range(self.simulation_elements):
            # For each time step, execute each device
            for device in simulation_devices:
                device.time_step(current_time=time_step,
                                 maximum_time=self.simulation_elements,
                                 sim_grid=self.simulation_grid,
                                 device_list=simulation_devices)
