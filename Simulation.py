from Map import Map
from Device import Device
import logging
from LoRa import LoRa
from LoRaE import LoRaE
from Sequence import Sequence

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
        """Get Simulation instance

        Raises:
            Exception: if Simulation class has not been instantiated yet

        Returns:
            Simulation: Simulation instance
        """
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
        time_sim, step, interval,
        number_runs, position_mode, time_mode,
        area_mode, payload_size, percentage,
        data_rate_lora, data_rate_lora_e
    ): 
        """Initializes Simulation instance as well as Lora and LoraE devices, Sequence object, and Map object.

        Args:
            size (int): Size of each simulation area side (i.e., x and y) in millimiters.
            devices (int): Number of total devices in the simulation.
            time_sim (int): Duration of the simulation in milliseconds.
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
            Exception: if Simulation class has been already instantiated
        """
    
        # Check instance exists
        if Simulation.__instance is not None:
            logger.fatal("Simulation class has already been instantiated!")
            raise Exception("Simulation class has already been instantiated!")

        # Assign instance
        Simulation.__instance = self

        self.simulation_duration = time_sim
        self.simulation_step = step
        self.simulation_map = Map(size, size, position_mode)
        
        num_devices_lora = int(devices * percentage)
        num_devices_lora_e = devices - num_devices_lora

        # Initialize LoRa and LoRa-E Devices
        lora_devices = []
        lora_e_devices = []
        for dev_id in range (num_devices_lora):
            lora_device = LoRa(
                            dev_id, data_rate_lora, payload_size,
                            interval, time_mode
                        )
            lora_devices.append(lora_device)

        dev_id_offset = len(lora_devices)

        for dev_id in range (num_devices_lora_e):
            lora_e_device = LoRaE(
                            dev_id_offset + dev_id, data_rate_lora_e, payload_size,
                            interval, time_mode
                        )
            lora_e_devices.append(lora_e_device)
        
        #Create Sequence if applicable
        if num_devices_lora_e != 0:
            mod_data = lora_e_devices[0].get_modulation_data()
            self.seq = Sequence(interval, mod_data["num_subch"], mod_data["data_rate"],
                                LoRaE.HOP_SEQ_N_BITS, 'lora-e-eu-hash', time_sim,
                                mod_data["hop_duration"], mod_data["num_usable_freqs"],
                                num_devices_lora_e)
            hop_seqs = self.seq.get_hopping_sequences()
            self.simulation_channels = mod_data["num_subch"]
            for i, dev in enumerate(lora_e_devices):
                if isinstance(dev, LoRaE):
                    dev.set_hopping_sequence(hop_seqs[i].tolist())

        elif num_devices_lora != 0:
            self.simulation_channels = lora_devices[0].get_modulation_data()["num_subch"]

        self.devices = lora_devices + lora_e_devices
        
        # Add devices positions to Map
        for dev in self.devices:
            self.simulation_map.add_device(dev.get_dev_id(), dev.get_position())

        # The simulation elements that have to be performed, where each element represents a millisecond
        self.simulation_elements = int(
            self.simulation_duration * self.simulation_step)

        # Create a zero-filled matrix with the number of elements and channels
        # TODO: initiallize array with custom type of tuple(int32, int32, int32) corresponding to (frame.owner, frame.number, frame.part_num)
        self.simulation_grid = np.zeros(
            (self.simulation_channels, int(self.simulation_elements)), dtype=(np.int32, 3))
        
    # Runs the simulation by calling the 'time_step' function of each device
    def run(self):
        """Runs the simulation
        """

        logger.info(
            f"Simulation time duration: {self.simulation_duration} milliseconds.")
        logger.info(
            f"Simulation time step: {self.simulation_step} milliseconds.")
        logger.info(
            f"Simulation device elements: {len(self.devices)} devices.")
        logger.info(
            f"Simulation channel elements: {self.simulation_channels} channels.")
        logger.info(
            f"Simulation total elements: {self.simulation_grid.shape}.")

        # Initialize the devices in the map
        for device in self.devices:
            next_time = device.generate_next_tx_time(0, self.simulation_elements)
            logger.debug("Node id={} scheduling at time={}.".format(device.get_dev_id(), next_time))
        
        # Run the simulation for each time step
        for time_step in range(self.simulation_elements):
            # For each time step, execute each device
            for device in self.devices:
                 # Check that the current time is the scheduled time of the device
                if time_step == device.get_next_tx_time():
                    logger.debug("Node id={} executing at time={}.".format(device.get_dev_id(), time_step))

                    frames = device.create_frame()
                    self.__allocate_frames(frames)
                    device.generate_next_tx_time(time_step, self.simulation_elements)
                    logger.debug("Node id={} scheduling at time={}.".format(device.get_dev_id(), device.get_next_tx_time()))


    def __allocate_frames(self, frames):
        """Allocates frames in the simulation grid

        Args:
            frames [(int, int, int, int, int, int)]: list of frames to be allocated in the grid
        """
        for frame in frames:
            # Get where to place
            freq, start, end, owner, number, part_num = frame

            if freq == -1:
                # Broadband transmission, modulation uses all BW of the channel
                freq = range(self.simulation_grid.shape[0])     

            # Check for a collision first
            collided = self.__check_collision(freq, start, end)

            # Place within the grid
            if (collided == True):
                frame_trace = (-1, 0, 0)
            else:
                # If no collision, frame should be placed with some information to trace it back, so 
                # this frame can be marked as collided when a collision happens later in simulation
                frame_trace = (owner, number, part_num)

            # Place the frame in the grid
            self.simulation_grid[freq, start:end] = frame_trace

    def __check_collision(self, freq, start, end):
        """Checks for collisions in the simulation_grid[freq, start:end]

        Args:
            freq (int_or_[int]): frequency index or slice in the simulation_grid
            start (int): start time index
            end (int): end time index

        Returns:
            bool: 1: there is a collision, 0:otherwise

        TODO:
            + Define a minimum frame overlap in Time domain to consider a collision
            + Define a minimum frame overlap in Frequency domain to consider a collision (needs freq resolution)
        """        
        # Create a grid view that covers only the area of interest of the frame (i.e., frequency and time)
        sim_grid_nodes  = self.simulation_grid[freq, start:end, 0]
        
        # Check if at least one of the slots in the grid view is being used
        is_one_slot_occupied = np.any(np.where(sim_grid_nodes != 0))

        # If at least one slot in the grid is occupied
        if is_one_slot_occupied:

            # Search the frames that have collided inside the grid view
            # Cells in the matrix can have the following values:
            # -1 if they have already COLLIDED
            #  0 if they are currently EMPTY
            # >0 if they are currently SUCCESSFUL
            collided_index = np.argwhere(sim_grid_nodes > 0)
            
            # If we have found collided frames
            if (len(collided_index > 0)):
                # Get the nodes, frames and subframes view from the sim_grid
                scratch_nodes     = self.simulation_grid[freq, start:end, 0]
                scratch_frames    = self.simulation_grid[freq, start:end, 1]
                scratch_subframes = self.simulation_grid[freq, start:end, 2]
                
                # When FHSS the resulting collided_index will be a row with the collision positions
                if (freq != range(self.simulation_grid.shape[0])):
                    print("FHSS {}".format(collided_index.shape))
                    for i in collided_index:
                        x = scratch_nodes[i]
                        assert(x > 0)
                
                # When CSS the resulting collided_index will be a 2D matrix with the collisions positions
                else:
                    print("CSS {}".format(collided_index.shape))
                    for index in collided_index:
                        i, j = index
                        x = scratch_nodes[i, j]
                        assert(x > 0)
        
        return False
