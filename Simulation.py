from Gateway import Gateway
from Map import Map
import logging
from LoRa import LoRa
from LoRaE import LoRaE
import os
import time

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
        self, size, devices_set_1, devices_set_2,
        time_sim, step, interval,
        run_number, position_mode, position_mode_values, time_mode,
        payload_size, use_ratios, lora_ratio, num_devices,
        data_rate_set_1, data_rate_set_2,
        auto_data_rate_lora, tx_power, lora_packet_loss_threshold,
        lora_e_packet_loss_threshold, save_simulation, dir_name
    ):
        """Initializes Simulation instance as well as Lora and LoraE devices, Sequence object, and Map object.

        Args:
            size (int): Size of each simulation area side (i.e., x and y) in meters.
            devices_set_1 (int): Number of devices for the first set in the simulation.
            devices_set_2 (int): Number of devices for the first set in the simulation.
            time_sim (int): Duration of the simulation in milliseconds.
            step (int): Time step of the simulation in milliseconds.
            interval (int): Transmit interval for each device (ms).
            run_number (int): Number of script run.
            position_mode (str): Node positioning mode (i.e., normal, uniform or annulus).
            position_mode_values [int]: inner radius and outer radius values for annulus position mode, std for normal position mode
            time_mode (str): Time error mode for transmitting devices (i.e., normal, uniform or exponential distribution).
            payload_size (int): Transmit payload of each device (bytes).
            use_ratios (int): Enables simulation using LoRa devices ratio instead of fixed numbers of LoRa/LoRa-E devices.
            lora_ratio (float): Ratio of LoRa devices in the simulation. Used when use_ratios=1.
            num_devices (int): Number of total devices to simulate. Used when use_ratios=1
            data_rate_set_1 (int): Data rate mode for devices in set 1.
            data_rate_set_2 (int): Data rate mode for devices in set 2.
            auto_data_rate_lora (bool): Whether LoRa data rate mode selection is automatic or not.
            tx_power (int): TX power of devices (dBm)
            lora_packet_loss_threshold (float): LoRa packet loss threshold.
            lora_e_packet_loss_threshold (float): LoRa-E packet loss threshold.
            save_simulation (bool): If True, generates grid and saves it as a PNG file.
            dir_name (str): Directory where simulation results will be stored

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
        self.simulation_map = Map(size, size, 0, position_mode, position_mode_values)

        # Instance variables used within parallelly executed routines
        self.data_rate_set_1 = data_rate_set_1
        self.data_rate_set_2 = data_rate_set_2
        self.auto_data_rate_lora = auto_data_rate_lora
        self.payload_size = payload_size
        self.interval = interval
        self.time_mode = time_mode
        self.use_ratios = use_ratios
        self.lora_ratio = lora_ratio
        self.num_devices = num_devices
        self.run_number = run_number
        self.lora_packet_loss_threshold = lora_packet_loss_threshold
        self.lora_e_packet_loss_threshold = lora_e_packet_loss_threshold
        self.num_devices_set_1 = devices_set_1
        self.num_devices_set_2 = devices_set_2
        self.modulation_devices_set_1 = 'LoRa' if data_rate_set_1 in range(0,6) else 'LoRaE'
        self.modulation_devices_set_2 = 'LoRa' if data_rate_set_2 in range(0,6) else 'LoRaE'
        self.save_simulation = save_simulation
        self.dir_name = dir_name
        self.tx_power = tx_power

        # Initialize Gateway

        self.gateway = Gateway(0, size)

        # Add gateway position to Map
        self.simulation_map.add_gateway(self.gateway.get_id(), self.gateway.get_position())

        # Initialize LoRa and LoRa-E Devices

        self.devices_set_1 = []
        self.devices_set_2 = []
       
        for dev_id in range(self.num_devices_set_1 if self.use_ratios == 0 else int(self.num_devices*self.lora_ratio)):
            if self.modulation_devices_set_1 == 'LoRa':
                device = LoRa(
                    dev_id, data_rate_set_1, payload_size,
                    interval, time_mode, lora_packet_loss_threshold,
                    self.simulation_map.generate_position(self.tx_power), self.tx_power,
                    self.gateway, self.auto_data_rate_lora
                )
            else:
                device = LoRaE(
                    dev_id, data_rate_set_1, payload_size,
                    interval, time_mode, lora_packet_loss_threshold,
                    self.simulation_map.generate_position(self.tx_power), self.tx_power,
                    self.gateway, self.auto_data_rate_lora
                )
            self.devices_set_1.append(device)

        dev_id_offset = devices_set_1

        for dev_id in range(self.num_devices_set_2 if self.use_ratios==0 else int((1-self.lora_ratio)*self.num_devices)):
            if self.modulation_devices_set_2 == 'LoRa':
                device = LoRa(
                    dev_id_offset + dev_id, data_rate_set_2, payload_size,
                    interval, time_mode, lora_packet_loss_threshold,
                    self.simulation_map.generate_position(self.tx_power), self.tx_power,
                    self.gateway, self.auto_data_rate_lora
                )
            else:
                device = LoRaE(
                    dev_id_offset + dev_id, data_rate_set_2, payload_size,
                    interval, time_mode, lora_e_packet_loss_threshold,
                    self.simulation_map.generate_position(self.tx_power), self.tx_power,
                    self.gateway
                )
            self.devices_set_2.append(device)
       
        self.devices = self.devices_set_1 + self.devices_set_2

        # Set simulation channels
        if all(isinstance(dev, LoRa) for dev in self.devices):
            # All devices are LoRa
            self.simulation_channels = self.devices[0].get_modulation_data()["num_subch"]
        else:
            # Some or all devices are LoRa-E
            lora_e_device = next(dev for dev in self.devices if isinstance(dev, LoRaE))
            self.simulation_channels = lora_e_device.get_modulation_data()["num_subch"]

        # Add devices positions to Map
        for dev in self.devices:
            self.simulation_map.add_device(
                dev.get_dev_id(), dev.get_position())

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


    def get_metrics(self):
        """
        Returns tuple of size 4 with received and generated packets for LoRa and LoRa-E devices
        """
        # Count generated and lost packets for each device in simulation
        devices = self.devices

        set_1_num_pkt_sent_list = []
        set_1_num_pkt_lost_list = []

        set_2_num_pkt_sent_list = []
        set_2_num_pkt_lost_list = []

        df = pd.DataFrame(columns=['dev_id', 'set', 'modulation', 'pkt_sent', 'pkt_lost', 'pkt_rx_power', 'pos_x', 'pos_y', 'pos_z'])
        
        for device in devices:
            
            sent_frames_count, lost_frames_count = device.calculate_metrics()

            if device in self.devices_set_1:    
                set_1_num_pkt_sent_list.append(sent_frames_count)
                set_1_num_pkt_lost_list.append(lost_frames_count)
                set = 1

            elif device in self.devices_set_2:
                set_2_num_pkt_sent_list.append(sent_frames_count)
                set_2_num_pkt_lost_list.append(lost_frames_count)
                set = 2

            x, y, z = device.get_position()
            df.loc[device.get_dev_id()] = [device.get_dev_id(), set, device.get_modulation_data()["mod_name"], sent_frames_count, lost_frames_count, device.get_rx_power(), x, y, z]

        # Calculate LoRa metrics
        if set_1_num_pkt_sent_list:
            n_coll_per_dev = np.nanmean(set_1_num_pkt_lost_list)
            n_gen_per_dev = np.nanmean(set_1_num_pkt_sent_list)
            n_rxed_per_dev = n_gen_per_dev - n_coll_per_dev
        else:
            n_gen_per_dev = 0.0
            n_rxed_per_dev = 0.0

        # Calculate LoRa-E metrics
        if set_2_num_pkt_sent_list:
            n_coll_per_dev_lora_e = np.nanmean(set_2_num_pkt_lost_list)
            n_gen_per_dev_lora_e = np.nanmean(set_2_num_pkt_sent_list)
            n_rxed_per_dev_lora_e = n_gen_per_dev_lora_e - n_coll_per_dev_lora_e
        else:
            n_gen_per_dev_lora_e = 0.0
            n_rxed_per_dev_lora_e = 0.0

        metrics = (n_rxed_per_dev, n_gen_per_dev,
                   n_rxed_per_dev_lora_e, n_gen_per_dev_lora_e)

        logger.debug(f'TOTAL NUM. GENERATED LORA PACKETS: {np.nansum(set_1_num_pkt_sent_list)}')
        logger.debug(f'TOTAL NUM. LOST LORA PACKETS: {np.nansum(set_1_num_pkt_lost_list)}')
        logger.debug(f'TOTAL NUM. GENERATED LORA-E PACKETS: {np.nansum(set_2_num_pkt_sent_list)}')
        logger.debug(f'TOTAL NUM. LOST LORA-E PACKETS: {np.nansum(set_2_num_pkt_lost_list)}')
        #logger.debug(f'GOODPUT:{(self.num_devices_lora+self.num_devices_lora_e)*self.payload_size*((self.percentage*n_rxed_per_dev*(4/5)) + ((1-self.percentage)*n_rxed_per_dev_lora_e*(1/3)))}')
        #print(f'GOODPUT: {(self.num_devices_lora+self.num_devices_lora_e)*self.payload_size*((self.percentage*n_rxed_per_dev*(4/5)) + ((1-self.percentage)*n_rxed_per_dev_lora_e*(1/3)))}')

        self.__save_simulation(df)
        #self.__plot_pkts_distr(lora_num_pkt_sent_list, lora_num_pkt_lost_list, lora_e_num_pkt_sent_list, lora_e_num_pkt_lost_list)
        return metrics

    def __save_simulation(self, df):
        if os.path.isfile(f'{self.dir_name}/r_{self.run_number}_.csv'):
            #File already exists. Append data
            df.to_csv(f'{self.dir_name}/r_{self.run_number}_.csv', mode='a', header=False, columns=['dev_id', 'set', 'modulation', 'pkt_sent', 'pkt_lost', 'pkt_rx_power', 'pos_x', 'pos_y', 'pos_z'])
        else:
            #File does not exist. Insert header and data
            df.to_csv(f'{self.dir_name}/r_{self.run_number}_.csv', mode='w', columns=['dev_id', 'set', 'modulation', 'pkt_sent', 'pkt_lost', 'pkt_rx_power', 'pos_x', 'pos_y', 'pos_z'])

    def __plot_pkts_distr(self, lora_num_pkt_sent_list, lora_num_pkt_lost_list, lora_e_num_pkt_sent_list, lora_e_num_pkt_lost_list):

        fig, (ax1, ax2) = plt.subplots(1,2)

        fig.suptitle("NOT Considering RX Power")

        #ax.hist(np.divide(lora_num_pkt_lost_list, lora_num_pkt_sent_list)*100, bins=max(lora_num_pkt_sent_list))
        ax1.bar(range(0, len(lora_num_pkt_sent_list)), np.divide(lora_num_pkt_lost_list, lora_num_pkt_sent_list)*100)
        ax1.set_title("(lost_packets / sent_packets)*100 ratio per device")
        ax1.set_xlabel("Device id")
        ax1.set_ylabel("(lost_packets / sent_packets)*100 ratio")
        
        hist_data = np.divide(lora_num_pkt_lost_list, lora_num_pkt_sent_list)*100
        ax2.hist(hist_data+5, bins=np.linspace(0,100,11)+5, density=True, rwidth=0.8)
        ax2.set_xticks(np.linspace(0,100,11))
        ax2.set_title("Lost packets ratio per device distribution")
        ax2.set_xlabel("Lost packets ratio")
        ax2.set_ylabel("Num. devices")
        ax2.set_xlim(-5, 105)

        plt.grid(True, alpha=0.5)
        plt.show()

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

        if self.save_simulation:
            self.__save_simulation()

        # Plot the Map. It shows both GW and nodes positions.
        # self.__plot_map()
       

    def __plot_map(self):
        '''Plot the Map. It shows both GW and nodes positions.
        '''
        fig, ax = plt.subplots(1)
        devs = self.simulation_map.get_devices_positions()
        gw = self.simulation_map.get_gateway_position()

        ax.scatter(gw[1][0], gw[1][1], c='red')
        for (_, (x,y,_)) in devs:
            ax.scatter(x,y,c='blue')
        ax.grid(True, alpha=0.5)
        fig.savefig('./images/simulated_map.png', format='png', dpi=200)
        plt.show()

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
            if collided:
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
                    try:
                        old_frame = self.devices[owner].frame_dict[number][part_n]
                        old_frame.set_collided(True)
                        # if not (old_frame.get_channel() == -1 and new_frame.get_channel() == -1):
                        # old_frame and new_frame are not LoRa.
                        old_frame.add_collided_frame(new_frame)
                        new_frame.add_collided_frame(old_frame)

                    except KeyError:
                        print(f'owner: {owner}, number: {number}, part_n:{part_n}')
                        print(f'self.devices length: {len(self.devices)}')
                    
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
        return self.num_devices_set_1

    def get_num_lora_e_devices(self):
        """Gets the number of LoRa-E devices

        Returns:
            (int): num of LoRa-E devices
        """
        return self.num_devices_set_2