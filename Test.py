import argparse
import configparser
import logging
import os
import sys

import numpy as np

import Codes
import Device
import Map
import Results
import Simulation

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('Test.cfg')


def get_options(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-d", "--devices", type=int, help="num devices")
    parser.add_argument("-t", "--interval", type=int, help="tx interval")
    parser.add_argument("-r", "--run", type=int, help="run")
    parser.add_argument("-tm", "--t_mode", help="time_mode")
    parser.add_argument("-pl", "--payload", type=int, help="tx payload in bytes")
    parser.add_argument("-dr", "--data_rate_mode", type=int, help="dr mode")
    options = parser.parse_args(args)
    return options


def main(options):
    logging.basicConfig(level=logging.CRITICAL, filename='Test.log', filemode='w',
                        format='%(filename)s:%(lineno)s %(levelname)s: %(message)s')

    # Determines if the simulation is random or deterministic
    is_random = config.getboolean('simulation', 'is_random')
    if not is_random:
        logger.info("Running simulation in random mode: {}".format(is_random))
        np.random.seed(seed=1714)

    map_size_x = config.getint('simulation', 'map_size_x')
    map_size_y = config.getint('simulation', 'map_size_y')

    device_position_mode = config.get('simulation', 'device_position_mode')
    simulation_duration = config.getint('simulation', 'simulation_duration')
    simulation_step = config.getint('simulation', 'simulation_step')

    device_count = options.devices
    device_time_mode = options.t_mode
    device_tx_interval = options.interval
    device_tx_payload = options.payload
    data_rate_mode = options.data_rate_mode

    if data_rate_mode == 8:
        print('LoRa-E DR8.')
        device_modulation = 'FHSS'
        simulation_channels = 280
        device_tx_rate = 162
        number_repetitions_header = 3
        numerator_coding_rate = 1
        hop_duration = 50
    elif data_rate_mode == 9:
        print('LoRa-E DR9.')
        device_modulation = 'FHSS'
        simulation_channels = 280
        device_tx_rate = 366
        number_repetitions_header = 2
        numerator_coding_rate = 2
        hop_duration = 50
    elif data_rate_mode == 11:
        print('LoRa-E DR11.')
        device_modulation = 'FHSS'
        simulation_channels = 688
        device_tx_rate = 366
        number_repetitions_header = 2
        numerator_coding_rate = 2
        hop_duration = 50
    else:
        print('LoRa.')
        device_modulation = 'notFHSS'
        simulation_channels = 1
        device_tx_rate = 0          # will be defined by SF
        number_repetitions_header = 1
        numerator_coding_rate = 0   # N/A
        hop_duration = 50

    # Create the map
    simulation_map = Map.Map(size_x=map_size_x, size_y=map_size_y, position_mode=device_position_mode)

    # Create the simulation
    simulation = Simulation.Simulation(simulation_duration=simulation_duration,
                                       simulation_step=simulation_step,
                                       simulation_channels=simulation_channels,
                                       simulation_map=simulation_map)

    # Create frequency hopping list
    code = Codes.Codes(modulation=device_modulation,
                       n_devices=device_count,
                       n_bits=9,
                       n_channels=simulation_channels,
                       n_hops=simulation_duration / hop_duration,
                       seq_type='lora-e-eu-cycle',
                       dr=data_rate_mode)

    # Create the devices and add them to the simulation
    for device_id in range(device_count):
        # Create device
        device = Device.Device(device_id=device_id,
                               time_mode=device_time_mode,
                               tx_interval=device_tx_interval,
                               tx_rate=device_tx_rate,
                               tx_payload=device_tx_payload,
                               modulation=device_modulation,
                               hop_duration=hop_duration,
                               hop_list=code.get_hopping_sequence(device_id),
                               num_rep_header=number_repetitions_header,
                               dr=data_rate_mode)
        # Add device to simulation
        simulation_map.add_device(device)

    # Run the simulation
    simulation.run()

    # Count collisions
    # Results.view_collisions(simulation, device_modulation, numerator_coding_rate)
    per = Results.get_num_rxed_gen_node(simulation, device_modulation, numerator_coding_rate)
    print(per)

    # create dir and save
    dir_name = './results/dr' + str(data_rate_mode) + '/pl' + str(device_tx_payload) + '/'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    np.save(dir_name + str(device_count) + '_' + str(device_tx_interval) + '_' + str(options.run), per)


if __name__ == "__main__":
    options = get_options(sys.argv[1:])
    if options.run is None:
        options.run = 0
    if options.interval is None:
        options.interval = 10000
    if options.devices is None:
        options.devices = 2
    if options.t_mode is None:
        options.t_mode = 'expo'
    if options.t_mode == 'max':
        options.interval = 'max'
    if options.data_rate_mode is None:
        options.data_rate_mode = 9
    if options.payload is None:
        options.payload = 10
    print(options)

    main(options)
