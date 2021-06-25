import multiprocessing
from numba.core.decorators import jit
from numba.np.ufunc import parallel
from numpy.core.fromnumeric import repeat
from Map import Map
from Device import Device
import logging
from LoRa import LoRa
from LoRaE import LoRaE
from Sequence import Sequence
from multiprocessing import Pool, Process, Queue
import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
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
            logger.fatal("Simulation class has not been instantiated yet!")
            raise Exception("Simulation class has not been instantiated yet!")

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
        
        # Instance variables used within parallel executed routines
        self.data_rate_lora = data_rate_lora
        self.data_rate_lora_e = data_rate_lora_e
        self.payload_size = payload_size
        self.interval = interval
        self.time_mode = time_mode

        num_devices_lora = int(devices * percentage)
        num_devices_lora_e = devices - num_devices_lora

        # Initialize LoRa and LoRa-E Devices

        # Process' pool for simulation parallelization
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

        lora_devices = pool.map(self.generate_LoRa_device, range(num_devices_lora))
        lora_e_devices = pool.map(self.generate_LoRaE_device, range(num_devices_lora, num_devices_lora+num_devices_lora_e))

        pool.close()

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

    def generate_LoRa_device(self, dev_id):
        lora_device = LoRa(
                            dev_id, self.data_rate_lora, self.payload_size,
                            self.interval, self.time_mode
                        )
        return lora_device

    def generate_LoRaE_device(self, dev_id):
        lora_e_device = LoRaE(
                            dev_id, self.data_rate_lora_e, self.payload_size,
                            self.interval, self.time_mode
                        )
        return lora_e_device

    
    def __save_simulation(self):
        """
        Save the grid and devices of simulation for debugging or later grid plots.
        """
        assert(self != None)
        
        np.save('grid.npy', self.simulation_grid.copy())
        np.save('devices.npy', self.devices)
        
        # Plot each packet using matplotlib rectangle  
        grid = self.simulation_grid.copy()
        devices = self.devices
        
        fig, ax = plt.subplots(1)

        for device in devices:
            pkts = device.get_frame_list()
            for pkt in pkts:
                start = pkt.get_start_time()
                end = pkt.get_end_time()
                freq = pkt.get_channel()
                width = end - start

                if freq == -1:
                    height = grid.shape[0]
                    freq = 0
                else:
                    height = 1

                if pkt.get_is_collided():
                    color = 'red'
                else:
                    color = 'royalblue'
                    
                rect = patches.Rectangle(
                    (start, freq),
                    width,
                    height,
                    linewidth=1,
                    linestyle="-",
                    edgecolor=color,
                    facecolor=color,
                    fill=True,
                    alpha=0.5,
                    antialiased=False,
                )

                ax.add_patch(rect)
        ax.set_title(f'Devices: {len(devices)}')
        ax.set_xlabel('Time (sec)', fontsize=12)
        ax.set_ylabel('Frequency (488 Hz channels)', fontsize=12)
        ax.set_xlim(0, grid.shape[1])
        ax.set_ylim(0, grid.shape[0])
        fig.savefig('./images/simulated_grid.png', format='png', dpi=200)

    def get_metrics(self):
        """
        Returns tuple of size 4 with received and generated packets for LoRa and LoRa-E devices
        """

        devices = self.devices

        # LoRa lists
        lora_num_pkt_sent_list = []
        lora_num_pkt_coll_list = []

        # LoRa-E lists
        lora_e_num_pkt_sent_list = []
        lora_e_num_pkt_coll_list = []

        # Count collisions for each device in simulation
        for device in devices:

            frames = device.get_frame_list()

            if device.get_modulation_data()["mod_name"] == 'FHSS':

                frame_count = device.get_frame_list_length()
                de_hopped_frames_count = 0
                collisions_count = 0

                # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided
                frame_index = 0
                while frame_index < frame_count:
                    this_frame = frames[frame_index]
                    if frame_index == 0:
                        assert this_frame.get_is_header()     # sanity check: first frame in list must be a header

                    # De-hop the frame to its original form
                    total_num_parts = this_frame.get_num_parts()
                    header_repetitions = this_frame.get_num_header_rep()
                    headers_to_evaluate = frames[frame_index:frame_index + header_repetitions]
                    pls_to_evaluate = frames[frame_index + header_repetitions:frame_index + total_num_parts]

                    # At least I need one header not collided
                    header_decoded = False
                    for header in headers_to_evaluate:
                        assert header.get_is_header()         # sanity check
                        if not header.get_is_collided():
                            header_decoded = True
                            break

                    if header_decoded:
                        # Check how many pls collided
                        collided_pls_time_count = 0
                        non_collided_pls_time_count = 0
                        for pl in pls_to_evaluate:
                            assert not pl.get_is_header()     # sanity check
                            if pl.get_is_collided():
                                collided_pls_time_count = collided_pls_time_count + pl.get_duration()
                            else:
                                non_collided_pls_time_count = non_collided_pls_time_count + pl.get_duration()

                        # Check for time ratio, equivalent to bit
                        calculated_ratio = float(non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                        if calculated_ratio < device.get_modulation_data()["numerator_codrate"] / 3:
                            de_hopped_frame_collided = True
                        else:
                            de_hopped_frame_collided = False
                    else:
                        de_hopped_frame_collided = True

                    # Prepare next iter
                    frame_index = frame_index + total_num_parts + 1
                    de_hopped_frames_count = de_hopped_frames_count + 1

                    # Increase collision count if frame can not be decoded
                    if de_hopped_frame_collided:
                        collisions_count = collisions_count + 1

                # Store device results
                lora_e_num_pkt_sent_list.append(de_hopped_frames_count)
                lora_e_num_pkt_coll_list.append(collisions_count)

                # Sanity check: de-hopped frames should be equal to the number of unique frame ids
                pkt_nums = [pkt.get_number() for pkt in frames]
                assert len(set(pkt_nums)) == de_hopped_frames_count

            elif device.get_modulation_data()["mod_name"] == 'CSS':
                # Straight-forward collision count
                # how many packets were sent by the device
                lora_num_pkt_sent_list.append(device.get_frame_list_length())

                # how many of them collided
                count = 0
                for pkt in frames:
                    if pkt.get_is_collided():
                        count += 1
                lora_num_pkt_coll_list.append(count)

        # Calculate LoRa metrics
        if lora_num_pkt_sent_list:
            n_coll_per_dev = np.nanmean(lora_num_pkt_coll_list)
            n_gen_per_dev = np.nanmean(lora_num_pkt_sent_list)
            n_rxed_per_dev = n_gen_per_dev - n_coll_per_dev
        else:
            n_gen_per_dev = None
            n_rxed_per_dev = None

        # Calculate LoRa-E metrics
        if lora_e_num_pkt_sent_list:
            n_coll_per_dev_lora_e = np.nanmean(lora_e_num_pkt_coll_list)
            n_gen_per_dev_lora_e = np.nanmean(lora_e_num_pkt_sent_list)
            n_rxed_per_dev_lora_e = n_gen_per_dev_lora_e - n_coll_per_dev_lora_e
        else:
            n_gen_per_dev_lora_e = None
            n_rxed_per_dev_lora_e = None
        #lora_pdr_network = 1. - sum(lora_num_pkt_coll_list) / sum(lora_num_pkt_sent_list) if lora_num_pkt_sent_list else None
        #lora_e_pdr_network = 1. - sum(lora_e_num_pkt_coll_list) / sum(lora_e_num_pkt_sent_list) if lora_e_num_pkt_sent_list else None

        metrics = (n_rxed_per_dev, n_gen_per_dev, n_rxed_per_dev_lora_e, n_gen_per_dev_lora_e)

        return metrics

    def generate_devices_tx_time(self, dev):
        next_time = dev.generate_next_tx_time(0, self.simulation_elements)
        logger.debug("Node id={} scheduling at time={}.".format(dev.get_dev_id(), next_time))
        return dev

    #Parallelize some loops
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
        
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        self.devices = pool.map(self.generate_devices_tx_time, iterable=self.devices)
        
        """
        for device in self.devices:
            next_time = device.generate_next_tx_time(0, self.simulation_elements)
            logger.debug("Node id={} scheduling at time={}.".format(device.get_dev_id(), next_time))
        """
        # Run the simulation for each time step
        #TODO: Try to apply parallelization to this part
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

        self.__save_simulation()


    def __allocate_frames(self, frames):
        """Allocates frames in the simulation grid

        Args:
            frames [Frame]: list of frames to be allocated in the grid
        """
        for frame in frames:
            # Get where to place
            freq = frame.get_channel()
            start = frame.get_start_time()
            end = frame.get_end_time()
            owner = frame.get_owner()
            number = frame.get_number()
            part_num = frame.get_part_num()

            if freq == -1:
                # Broadband transmission, modulation uses all BW of the channel
                freq = range(self.simulation_grid.shape[0])     

            # Check for a collision first
            collided = self.__check_collision(frame, freq, start, end)

            # Place within the grid
            if (collided == True):
                frame_trace = (-1, 0, 0)
            else:
                # If no collision, frame should be placed with some information to trace it back, so 
                # this frame can be marked as collided when a collision happens later in simulation
                frame_trace = (owner, number, part_num)

            # Place the frame in the grid
            self.simulation_grid[freq, start:end] = frame_trace

    def __check_collision(self, frame, freq, start, end):
        """Checks for collisions in the simulation_grid[freq, start:end]

        Args:
            frame (Frame): frame instance
            freq (int_or_[int]): frequency index or slice in the simulation_grid
            start (int): start time index
            end (int): end time index

        Returns:
            bool: 1-> there is a collision, 0->otherwise

        TODO:
            + Define a minimum frame overlap in Time domain to consider a collision
            + Define a minimum frame overlap in Frequency domain to consider a collision (needs freq resolution
            + Coexistence LoRa and LoRa-E. 
                Replace simulation_grid 3-tuple elements with Frame (actually addresses to them).
                

        """        
        # Create a grid view that covers only the area of interest of the frame (i.e., frequency and time)
        sim_grid_nodes  = self.simulation_grid[freq, start:end, 0]

        # Check if at least one of the slots in the grid view is being used
        is_one_slot_occupied = np.any(np.where(sim_grid_nodes != 0))

        # If at least one slot in the grid is occupied
        if is_one_slot_occupied:

            frame.set_collided(True)
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
        
        else:
            frame.set_collided(False)

        return False

    def get_simulation_grid(self):
        """Gets the simulation grid

        Returns:
            matrix: returns a matrix of shape (sim_channels, sim_elements, 3)
        """
        return self.simulation_grid

    def get_device_list(self):
        """Gets device list

        Returns:
            [Device]: list of devices instances
        """
        return self.devices