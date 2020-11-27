import argparse
import configparser
import logging
import os
import random
import sys

import numpy as np

import Device
import LoraHelper
import Map
import Results
import Sequence
import Simulation

logger = logging.getLogger(__name__)

logging_name = "Simulator"
logging_ext  = ".log"
logging_mode = logging.DEBUG

config_name = "Simulator"
config_ext  = ".cfg"


def get_options(args=None):
    # If we don't pass argument list, get from standard input
    if args is None:
        args = sys.argv[1:]

    # Create parameter parser
    parser = argparse.ArgumentParser(description="WiNe Simulator for LoRa/LoRa_E networks.")

    # Add parameters to parser
    parser.add_argument("-d", "--devices", type=int, default=2, help="Number of total devices in the simulation.")
    parser.add_argument("-t", "--interval", type=int, default=1000, help="Transmit interval for each device (ms).")
    parser.add_argument("-r", "--run", type=int, default=0, help="Number of replication.")
    parser.add_argument("-tm", "--t_mode", type=str, default='normal', help="time_mode")
    parser.add_argument("-pl", "--payload", type=int, default=15, help="Transmit payload of each device (bytes).")
    parser.add_argument("-dr", "--data_rate_mode", default=8, type=int, help="LoRa data rate mode.")
    parser.add_argument("-l", "--logging_file", type=str, default='test', help="Logging filename.")

    # Parse arguments
    options = parser.parse_args(args)

    if options.t_mode == 'max':
        # we want the file name to contain max when tx at max rate
        options.interval = 'max'
    
    return options


def main(options, dir_name):
    # Read the basic simulator configuration
    config = configparser.ConfigParser()
    config_file = config_name + config_ext
    config.read(config_file)

    # Create logging object, will append to existing files
    logging_file = options.logging_file + logging_ext
    logging.basicConfig(level=logging_mode, filename=logging_file, filemode='w',
                        format='%(filename)s:%(lineno)s %(levelname)s: %(message)s')

    logger.info("Starting simulation with parameters = {}".format(options))

    # Determines if the simulation is random or deterministic
    is_random = config.getboolean('simulation', 'is_random')
    if not is_random:
        logger.info("Running simulation in random mode: {}".format(is_random))
        np.random.seed(seed=1714)
        random.seed(1714)

    # Determines the size of the map
    map_size_x = config.getint('simulation', 'map_size_x')
    map_size_y = config.getint('simulation', 'map_size_y')

    # Determines the device position mode (i.e., )
    device_position_mode = config.get('simulation', 'device_position_mode')

    # Determines the simulation duration (in milliseconds)
    simulation_duration = config.getint('simulation', 'simulation_duration')
    
    # Determines the simulation step (in milliseconds)
    simulation_step = config.getint('simulation', 'simulation_step')

    # Sets the number of devices, timing mode, transmit interval, payload and DR mode
    device_count       = options.devices
    device_time_mode   = options.t_mode
    device_tx_interval = options.interval
    device_tx_payload  = options.payload
    data_rate_mode     = options.data_rate_mode

    # Get LoRa/LoRa_E configuration
    # +++ TODO +++: this should be done by each device
    (
        device_modulation,
        simulation_channels,
        device_tx_rate,
        number_repetitions_header,
        numerator_coding_rate,
        hop_duration,
    ) = LoraHelper.LoraHelper.get_configuration(data_rate_mode)

    # Create the map
    simulation_map = Map.Map(size_x=map_size_x, size_y=map_size_y, position_mode=device_position_mode)

    # Create the simulation
    simulation = Simulation.Simulation(simulation_duration = simulation_duration,
                                       simulation_step     = simulation_step,
                                       simulation_channels = simulation_channels,
                                       simulation_map      = simulation_map)

    # Pre-compute frequency hopping sequences
    if device_tx_interval == 'max':
        # we can use the number of transmissions to pre-allocate memory
        # +++ TODO +++: calculate this exactly
        max_hops = simulation_duration / 4000 * hop_duration
    else:
        max_hops = simulation_duration / device_tx_interval * hop_duration

    seqs = Sequence.Sequence(modulation = device_modulation,
                             n_devices  = device_count,
                             n_bits     = 9,
                             n_channels = simulation_channels,
                             n_hops     = max_hops,
                             seq_type   = 'lora-e-eu-hash',
                             dr         = data_rate_mode)

    # Create the devices and add them to the simulation
    for device_id in range(device_count):
        # Create device
        device = Device.Device(device_id      = device_id,
                               time_mode      = device_time_mode,
                               tx_interval    = device_tx_interval,
                               tx_rate        = device_tx_rate,
                               tx_payload     = device_tx_payload,
                               modulation     = device_modulation,
                               hop_duration   = hop_duration,
                               hop_list       = seqs.get_hopping_sequence(device_id),
                               num_rep_header = number_repetitions_header,
                               dr             = data_rate_mode)

        # Add device to simulation
        simulation_map.add_device(device)

    # Run the simulation
    simulation.run()

    # Count collisions
    #Results.view_collisions(simulation, device_modulation, numerator_coding_rate)
    #raise Exception('does not save results/sim duration not 1h')
    per = Results.get_num_rxed_gen_node(simulation, device_modulation, numerator_coding_rate)

    # Save the NumPy results to file
    np.save(dir_name + str(device_count) + '_' + str(device_tx_interval) + '_' + str(options.run), per)


if __name__ == "__main__":
    # Get the execute parameters
    options = get_options()

    # Create directory if it does not exist
    dir_name = './results/dr' + str(options.data_rate_mode) + '/pl' + str(options.payload) + '/'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Run simulation
    main(options, dir_name)
