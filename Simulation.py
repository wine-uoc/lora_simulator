from Gateway import Gateway
from multiprocessing import Array
from numpy.core.fromnumeric import repeat
from Map import Map
from Device import Device
import logging
from LoRa import LoRa
from LoRaE import LoRaE
from Sequence import Sequence
from multiprocessing import Pool, Process, Queue
import os
import time
import functools

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

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
        data_rate_lora, data_rate_lora_e,
        auto_data_rate_lora
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
            auto_data_rate_lora (bool): Whether LoRa data rate mode selection is automatic or not.

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

        # Instance variables used within parallelly executed routines
        self.data_rate_lora = data_rate_lora
        self.data_rate_lora_e = data_rate_lora_e
        self.auto_data_rate_lora = auto_data_rate_lora
        self.payload_size = payload_size
        self.interval = interval
        self.time_mode = time_mode

        self.num_devices_lora = int(devices * percentage)
        self.num_devices_lora_e = devices - self.num_devices_lora

        # Initialize Gateway

        self.gateway = Gateway(0, size, area_mode)

        # Initialize LoRa and LoRa-E Devices

        lora_devices = []
        lora_e_devices = []
        for dev_id in range(self.num_devices_lora):
            lora_device = LoRa(
                dev_id, data_rate_lora, payload_size,
                interval, time_mode, self.gateway if self.auto_data_rate_lora else None
            )
            lora_devices.append(lora_device)

        dev_id_offset = len(lora_devices)

        for dev_id in range(self.num_devices_lora_e):
            lora_e_device = LoRaE(
                dev_id_offset + dev_id, data_rate_lora_e, payload_size,
                interval, time_mode
            )
            lora_e_devices.append(lora_e_device)
        
        # Set simulation channels
        if self.num_devices_lora_e != 0:
            self.simulation_channels = lora_e_devices[0].get_modulation_data()["num_subch"]
        elif self.num_devices_lora != 0:
            self.simulation_channels = lora_devices[0].get_modulation_data()["num_subch"]

        self.devices = lora_devices + lora_e_devices

        # Add devices positions to Map
        for dev in self.devices:
            self.simulation_map.add_device(
                dev.get_dev_id(), dev.get_position())

        # Add gateway position to Map

        self.simulation_map.add_gateway(self.gateway.get_id(), self.gateway.get_position())

        # The simulation elements that have to be performed, where each element represents a millisecond
        self.simulation_elements = int(
            self.simulation_duration * self.simulation_step)

        # Create a zero-filled matrix with the number of elements and channels
       
        self.simulation_grid = np.zeros(
            (self.simulation_channels, int(self.simulation_elements)), dtype=(np.uint16, 3))

    def __save_simulation(self):
        """
        Save the grid and devices of simulation for debugging or later grid plots.
        """
        assert(self != None)

        #np.save('grid.npy', self.simulation_grid)
        #np.save('devices.npy', self.devices)

        # Plot each packet using matplotlib rectangle
        grid = self.simulation_grid
        devices = self.devices

        fig, ax = plt.subplots(1)

        for device in devices:
            frames_dict = device.get_frame_dict()
            for frame_key in frames_dict:
                pkts = frames_dict[frame_key]
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
                        linewidth=0.0,
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
        logger.info("Simulation grid image saved!")

    def compute_metrics(self, devices, lora_e_num_pkt_coll_list, lora_e_num_pkt_sent_list, lora_num_pkt_coll_list, lora_num_pkt_sent_list):
        for device in devices:
            id = device.get_dev_id()
            if device.get_modulation_data()["mod_name"] == 'FHSS':
                if id >= self.num_devices_lora:
                    id = self.num_devices_lora - id

                #frame_count = len(frames_list)
                de_hopped_frames_count = 0
                collisions_count = 0

                # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided
                frames_dict = device.get_frame_dict()
                for frame_key in frames_dict:
                    frames_list = frames_dict[frame_key]
                    #frame_count = len(frames_list)
                    #frame_index = 0
                    #this_frame = frames_list[0]
            
                    # sanity check: first frame in list must be a header
                    assert frames_list[0].get_is_header()

                    # De-hop the frame to its original form
                    total_num_parts = frames_list[0].get_num_parts()
                    header_repetitions = frames_list[0].get_num_header_rep()
                    headers_to_evaluate = frames_list[:header_repetitions]
                    pls_to_evaluate = frames_list[header_repetitions:total_num_parts]

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
                        calculated_ratio = float(
                            non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                        if calculated_ratio < device.get_modulation_data()["numerator_codrate"] / 3:
                            de_hopped_frame_collided = True
                        else:
                            de_hopped_frame_collided = False
                    else:
                        de_hopped_frame_collided = True

                    # Prepare next iter
                    #frame_index = frame_index + total_num_parts + 1
                    de_hopped_frames_count = de_hopped_frames_count + 1

                    # Increase collision count if frame can not be decoded
                    if de_hopped_frame_collided:
                        collisions_count = collisions_count + 1

                # Store device results
                lora_e_num_pkt_sent_list[id] = de_hopped_frames_count
                lora_e_num_pkt_coll_list[id] = collisions_count

                # Sanity check: de-hopped frames should be equal to the number of unique frame ids
                pkt_nums = [int(frame_key) for frame_key in frames_dict.keys()]
                assert len(set(pkt_nums)) == de_hopped_frames_count

            elif device.get_modulation_data()["mod_name"] == 'CSS':
                # Straight-forward collision count
                # how many packets were sent by the device
                lora_num_pkt_sent_list[id] = device.get_frame_dict_length()
                frames = device.get_frame_dict().values()
                frames_list = sum(frames, [])
                # how many of them collided
                count = 0
                for pkt in frames_list:
                    if pkt.get_is_collided():
                        count += 1
                lora_num_pkt_coll_list[id] = count

            #return device.get_frame_dict_length(), count, 0, 0

    def get_metrics(self):
        """
        Returns tuple of size 4 with received and generated packets for LoRa and LoRa-E devices
        """
        '''
        ini = time.time_ns()

        # LoRa lists
        lora_num_pkt_sent_list = Array(typecode_or_type='i', size_or_initializer=self.num_devices_lora, lock=False)
        lora_num_pkt_coll_list = Array(typecode_or_type='i', size_or_initializer=self.num_devices_lora, lock=False)

        # LoRa-E lists
        lora_e_num_pkt_sent_list = Array(typecode_or_type='i', size_or_initializer=self.num_devices_lora_e, lock=False)
        lora_e_num_pkt_coll_list = Array(typecode_or_type='i', size_or_initializer=self.num_devices_lora_e, lock=False)
        
        
        num_cpus = os.cpu_count()
        devs_per_cpu = round(len(self.devices) / num_cpus)
        devs = [self.devices[k:k+devs_per_cpu] for k in range(0, len(self.devices), devs_per_cpu)]
        processes = [Process(target=self.compute_metrics, args=(devs[i], 
                                                                lora_e_num_pkt_coll_list, 
                                                                lora_e_num_pkt_sent_list,
                                                                lora_num_pkt_coll_list,
                                                                lora_num_pkt_sent_list)) for i in range(len(devs))]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        
        elapsed = time.time_ns() - ini
        
        '''
        # Count collisions for each device in simulation
        ini = time.time_ns()
        devices = self.devices

        # LoRa lists
        lora_num_pkt_sent_list = []
        lora_num_pkt_coll_list = []

        # LoRa-E lists
        lora_e_num_pkt_sent_list = []
        lora_e_num_pkt_coll_list = []

        lora_num_collisions_per_pkt_coll = []

        for device in devices:

            if device.get_modulation_data()["mod_name"] == 'FHSS':

                #frame_count = len(frames_list)
                de_hopped_frames_count = 0
                collisions_count = 0

                # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided

                frames_dict = device.get_frame_dict()
                for frame_key in frames_dict:
                    frames_list = frames_dict[frame_key]
                    #frame_count = len(frames_list)
                    #frame_index = 0
                    #this_frame = frames_list[0]
            
                    # sanity check: first frame in list must be a header
                    assert frames_list[0].get_is_header()

                    # De-hop the frame to its original form
                    total_num_parts = frames_list[0].get_num_parts()
                    header_repetitions = frames_list[0].get_num_header_rep()
                    headers_to_evaluate = frames_list[:header_repetitions]
                    pls_to_evaluate = frames_list[header_repetitions:total_num_parts]

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
                        calculated_ratio = float(
                            non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                        if calculated_ratio < device.get_modulation_data()["numerator_codrate"] / 3:
                            de_hopped_frame_collided = True
                        else:
                            de_hopped_frame_collided = False
                    else:
                        de_hopped_frame_collided = True

                    # Prepare next iter
                    #frame_index = frame_index + total_num_parts + 1
                    de_hopped_frames_count = de_hopped_frames_count + 1

                    # Increase collision count if frame can not be decoded
                    if de_hopped_frame_collided:
                        collisions_count = collisions_count + 1

                # Store device results
                lora_e_num_pkt_sent_list.append(de_hopped_frames_count)
                lora_e_num_pkt_coll_list.append(collisions_count)

                # Sanity check: de-hopped frames should be equal to the number of unique frame ids
                pkt_nums = [int(frame_key) for frame_key in frames_dict.keys()]
                assert len(set(pkt_nums)) == de_hopped_frames_count

            elif device.get_modulation_data()["mod_name"] == 'CSS':
                # Straight-forward collision count
                # how many packets were sent by the device
                lora_num_pkt_sent_list.append(device.get_frame_dict_length())
                frames = device.get_frame_dict().values()
                frames_list = sum(frames, [])
                # how many of them collided
                count = 0
                for pkt in frames_list:
                    lora_num_collisions_per_pkt_coll.append(len(pkt.get_collided_intervals()))
                    if pkt.get_is_collided():
                        count += 1
                        logger.debug(f'FRAME: ({pkt.get_owner()},{pkt.get_number()},{pkt.get_part_num()}) --> Collided intervals: {pkt.get_collided_intervals()}')
                lora_num_pkt_coll_list.append(count)
        elapsed = time.time_ns() - ini
        data = pd.Series(lora_num_collisions_per_pkt_coll)
        data.to_csv('lora_packets_collisions.csv')
        print(data)
        
        logger.info(f'get_metrics time: {elapsed/1000000.0} ms')
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

        metrics = (n_rxed_per_dev, n_gen_per_dev,
                   n_rxed_per_dev_lora_e, n_gen_per_dev_lora_e)

        return metrics

    # Parallelize some loops

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

        # Generate initial tx times for each device
        for device in self.devices:
            next_time = device.generate_next_tx_time(
                0, self.simulation_elements)
            logger.debug("Node id={} scheduling at time={}.".format(
                device.get_dev_id(), next_time))

        # Run the simulation for each time step
        # TODO: Try to apply parallelization to this part???
        ini = round(time.time() * 1000)

        # Sort devices by tx_time in ascending order. Remove those whose tx_time == np.inf
        devices = self.devices.copy()
        devices.sort(key=lambda d: d.next_time)
        found = False
        for i, d in enumerate(devices):
            if d.get_next_tx_time() == np.inf:
                found = True
                break

        if not found:
            devices = devices[:i+1]
        else:        
            devices = devices[:i]

        while len(devices) != 0:
            dev = devices[0]
            curr_time_step = dev.get_next_tx_time()

            logger.debug("Node id={} executing at time={}.".format(
                dev.get_dev_id(), curr_time_step))
            frames = dev.create_frame()
            self.__allocate_frames(frames)
            dev.generate_next_tx_time(curr_time_step, self.simulation_elements)
            logger.debug("Node id={} scheduling at time={}.".format(
                dev.get_dev_id(), dev.get_next_tx_time()))

            # Prepare for next iteration
            dev_next_tx_time = dev.get_next_tx_time()
            if dev_next_tx_time == np.inf:
                del devices[0]
            else:
                found = False
                for i, d in enumerate(devices):
                    if d.get_next_tx_time() > dev_next_tx_time:
                        found = True
                        break

                if not found:
                    devices.insert(i+1, dev)
                else:        
                    devices.insert(i, dev)
                del devices[0]
                
                        
           # dev = devices[0]
           # curr_time_step = dev.get_next_tx_time()

        elapsed = round(time.time() * 1000) - ini
        logger.debug(f'elapsed time: {elapsed} ms')

        #self.__save_simulation()

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
                #frame_trace = (-1, 0, 0)
                frame_trace = (owner, number, part_num)
            else:
                # If no collision, frame should be placed with some information to trace it back, so
                # this frame can be marked as collided when a collision happens later in simulation
                frame_trace = (owner, number, part_num)

            # Place the frame in the grid
            self.simulation_grid[freq, start:end] = frame_trace

    def __check_collision(self, new_frame, freq, start_new, end_new):
        """Checks for collisions in the simulation_grid[freq, start:end]. 
        If a collision occurs, mark appropriate frames as collided.

        Args:
            new_frame (Frame): frame instance
            freq (int_or_[int]): frequency index or slice in the simulation_grid
            start_new (int): start time index
            end_new (int): end time index

        Returns:
            bool: 1-> there is a collision, 0->otherwise

        TODO:
            + Define a minimum frame overlap in Time domain to consider a collision
            + Define a minimum frame overlap in Frequency domain to consider a collision (needs freq resolution)
        """
        # Create a grid view that covers only the area of interest of the frame (i.e., frequency and time)
        sim_grid_nodes = self.simulation_grid[freq, start_new:end_new, 0]

        # Check if at least one of the slots in the grid view is being used
        is_one_slot_occupied = np.any(np.where(sim_grid_nodes != 0))

        # If at least one slot in the grid is occupied
        if is_one_slot_occupied:

            new_frame.set_collided(True)
            # Search the frames that have collided inside the grid view
            # Cells in the matrix can have the following values:
            # -1 if they have already COLLIDED
            #  0 if they are currently EMPTY
            # >0 if they are currently SUCCESSFUL

            grid_view = self.simulation_grid[freq, start_new:end_new]
            try:
                len(freq)
            except TypeError:
                flattened_grid = grid_view.reshape(end_new-start_new, -1)
            else:
                flattened_grid = grid_view.reshape(len(freq)*(end_new-start_new), -1)

            ini_alloc = round(time.time_ns())  # REMOVE LATER
            unique_grid = np.unique(flattened_grid, axis=0)  # Bottle neck
            elapsed_alloc = round(time.time_ns()) - ini_alloc  # REMOVE LATER
            for owner, number, part_n in unique_grid:
                if owner != 0:
                    old_frame = self.devices[owner].frame_list[number][part_n]
                    old_frame.set_collided(True)
                    
                    if  (old_frame.get_channel() == -1 and new_frame.get_channel() != -1) or \
                        (old_frame.get_channel() != -1 and new_frame.get_channel() == -1):
                        
                        start_old = old_frame.get_start_time()
                        end_old = old_frame.get_end_time()

                        old_frame.add_collided_frame_interval(start_new, end_new)
                        new_frame.add_collided_frame_interval(start_old, end_old)
                    
            logger.debug(f'coll idx time: {elapsed_alloc} ns, collided packets: {len(unique_grid)}')
            return True

        else:
            new_frame.set_collided(False)
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

    def get_num_lora_devices(self):
        """Gets the number of LoRa devices

        Returns:
            (int): num of LoRa devices
        """
        return self.num_devices_lora

    def get_num_lora_e_devices(self):
        """Gets the number of LoRa-E devices

        Returns:
            (int): num of LoRa-E devices
        """
        return self.num_devices_lora_e