import argparse
import configparser
import logging
import os
import random
import sys

import numpy as np

import Device
import Gateway
import LoraHelper
import Map
import Results
import Sequence
import Simulation
import SimulatorHelper

logger = logging.getLogger(__name__)

logging_name = "Simulator"
logging_ext  = ".log"
logging_mode = logging.CRITICAL

config_name = "Simulator"
config_ext  = ".cfg"


def get_options(args=None):
    # If we don't pass argument list, get from standard input
    if args is None:
        args = sys.argv[1:]

    # Create parameter parser
    parser = argparse.ArgumentParser(description="WiNe Simulator for LoRa/LoRa_E networks.")

    # Add parameters to parser
    parser.add_argument("-d", "--devices", type=int, default=10, help="Number of total devices in the simulation.")
    parser.add_argument("-t", "--interval", type=int, default=1000, help="Transmit interval for each device (ms).")
    parser.add_argument("-r", "--run", type=int, default=0, help="Number of script run.")
    parser.add_argument("-tm", "--t_mode", type=str, default='max', help="time_mode")
    parser.add_argument("-pl", "--payload", type=int, default=15, help="Transmit payload of each device (bytes).")
    parser.add_argument("-l", "--logging_file", type=str, default='log', help="Logging filename.")

    parser.add_argument("-p", "--percentage", default=0.5, type=float, help="Percentage of LoRa devices wrt LoRa-E (1 is all LoRa).")
    parser.add_argument("-dra", "--data_rate_lora", default=0, type=int, help="LoRa data rate mode.")
    parser.add_argument("-dre", "--data_rate_lora_e", default=8, type=int, help="LoRa-E data rate mode.")

    # Parse arguments
    options = parser.parse_args(args)

    if options.t_mode == 'max':
        # We want the file name to contain max when transmitting at max rate, but
        # in fact, the interval during simulation will be the minimun allowed by duty cycle regulation
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

    logger.info(f"Starting simulation with parameters = {options}")
    logger.info(f"Results will be saved in {dir_name}")

    # Determine if the simulation is random or deterministic
    is_random = config.getboolean('simulation', 'is_random')
    if not is_random:
        logger.info(f"Running simulation in random mode: {is_random}")
        np.random.seed(seed=1714)
        random.seed(1714)

    # Determines the size of the map
    map_size_x = config.getint('simulation', 'map_size_x')
    map_size_y = config.getint('simulation', 'map_size_y')

    # Determines the device position mode
    device_position_mode = config.get('simulation', 'device_position_mode')

    # Determines the simulation duration (in milliseconds)
    simulation_duration = config.getint('simulation', 'simulation_duration')
    
    # Determines the simulation step (in milliseconds)
    simulation_step = config.getint('simulation', 'simulation_step')

    # Sets the number of devices, timing mode, transmit interval, payload and DR mode
    device_count        = options.devices
    device_count_lora   = round(options.percentage * device_count)
    device_count_lora_e = device_count - device_count_lora
    data_rate_lora      = options.data_rate_lora
    data_rate_lora_e    = options.data_rate_lora_e

    device_time_mode    = options.t_mode
    device_tx_interval  = options.interval
    device_tx_payload   = options.payload

    # Get LoRaWAN configuration
    param_list_lora = LoraHelper.LoraHelper.get_configuration(data_rate_lora)
    param_list_lora_e = LoraHelper.LoraHelper.get_configuration(data_rate_lora_e)

    # Create the map
    simulation_map = Map.Map(size_x=map_size_x, size_y=map_size_y, position_mode=device_position_mode)

    # Create the simulation
    simulation = Simulation.Simulation(simulation_duration = simulation_duration,
                                       simulation_step     = simulation_step,
                                       # try to use LoRa-E frequency resolution for the simulation grid
                                       simulation_channels = param_list_lora_e[1] if device_count_lora_e > 0 else param_list_lora[1],
                                       simulation_map      = simulation_map)

    # Create a gateway
    gateway = Gateway.Gateway(uid=0)
    gateway.place_mid(sim_map=simulation.simulation_map)
    gateway.set_sf_thresholds(mode='equal')
    gateway.set_update_dr(state=False)

    # Create the devices, first LoRa then LoRa-E 
    devices_lora = SimulatorHelper.create_devices(parameter_list = param_list_lora, 
                                                  num_devices    = device_count_lora, 
                                                  data_rate      = data_rate_lora,
                                                  time_mode      = device_time_mode, 
                                                  tx_interval    = device_tx_interval, 
                                                  tx_payload     = device_tx_payload,
                                                  gateway        = gateway)
                                                  
    devices_lora_e = SimulatorHelper.create_devices(parameter_list  = param_list_lora_e, 
                                                    num_devices     = device_count_lora_e, 
                                                    data_rate       = data_rate_lora_e,
                                                    time_mode       = device_time_mode, 
                                                    tx_interval     = device_tx_interval, 
                                                    tx_payload      = device_tx_payload, 
                                                    offset_id       = device_count_lora,
                                                    pre_compute_seq = True,
                                                    sim_duration    = simulation_duration)

    # Add devices to simulation
    for device in devices_lora + devices_lora_e:
        simulation_map.add_device(device)

    # Run the simulation
    simulation.run()

    # Save simulation
    print("Saving ...")
    Results.save_simulation(simulation=simulation, save_sim=False, plot_grid=False)

    # Calculate and save metrics for LoRa and LoRa-E to file
    metrics = Results.get_metrics(simulation)
    np.save(dir_name + str(device_count) + '_' + str(device_tx_interval) + '_' + str(options.run), metrics)


if __name__ == "__main__":
    # Get the execute parameters
    options = get_options()

    # Create saving directory if it does not exist
    dir_name = SimulatorHelper.create_save_dir(options)

    # Run simulation
    main(options, dir_name)
