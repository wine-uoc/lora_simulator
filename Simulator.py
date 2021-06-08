import argparse
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

logger       = logging.getLogger(__name__)
logging_mode = logging.DEBUG

def get_options(args=None):
    # If we don't pass argument list, get from standard input
    if args is None:
        args = sys.argv[1:]

    # Create parameter parser
    parser = argparse.ArgumentParser(description="WiNe Simulator for LoRa/LoRa_E networks.")

    # Add parameters to parser
    parser.add_argument("-s", "--size", type=int, default=5000000, help="Size of each simulation area side (i.e., x and y) in millimiters.")
    parser.add_argument("-d", "--devices", type=int, default=100, help="Number of total devices in the simulation.")
    parser.add_argument("-t", "--time", type=int, default=36000, help="Duration of the simulation in milliseconds.")
    parser.add_argument("-st", "--step", type=int, default=1, help="Time step of the simulation in milliseconds.")
    parser.add_argument("-i", "--interval", type=int, default=10000, help="Transmit interval for each device (ms).")
    parser.add_argument("-n", "--number", type=int, default=0, help="Number of script run.")
    parser.add_argument("-pm", "--position_mode", type=str, default='normal', help="Node positioning mode (i.e., normal distribution or uniform distribution).")
    parser.add_argument("-tm", "--time_mode", type=str, default='max', help="Time error mode for transmitting devices (i.e., normal, uniform or exponential distribution). Using 'max' forces maximum data rate with exponential distribution.")
    parser.add_argument("-am", "--area_mode", type=str, default='distance', help="Area mode to assign DR (i.e., circles with equal distance or circles with equal area).")
    parser.add_argument("-pl", "--payload", type=int, default=15, help="Transmit payload of each device (bytes).")
    parser.add_argument("-l", "--logging_file", type=str, default='Simulator.log', help="Name of the logging filename.") 
    parser.add_argument("-r", "--random", type=bool, default=True, help="Determines if the simulation is random or deterministic (i.e., True is random).")
    parser.add_argument("-p", "--percentage", type=int, default=0.5, help="Percentage of LoRa devices with respect to LoRa-E (i.e., 1.0 is all LoRa devices).")
    parser.add_argument("-dra", "--data_rate_lora", type=int, default=0, help="LoRa data rate mode.")
    parser.add_argument("-dre", "--data_rate_lora_e", type=int, default=8, help="LoRa-E data rate mode.")

    # Parse arguments
    options = parser.parse_args(args)

    # We want the file name to contain max when transmitting at max rate, but
    # in fact, the interval during simulation will be the minimum allowed by duty cycle regulation
    if options.time_mode == 'max':    
        options.interval = 'max'
    
    return options


def main(options, dir_name):
    # Create logging object, will append to existing files
    logging_file = options.logging_file
    logging.basicConfig(level=logging_mode, filename=logging_file, filemode='w',
                        format='%(filename)s:%(lineno)s %(levelname)s: %(message)s')

    logger.info(f"Starting simulation with parameters = {options}")
    logger.info(f"Results will be saved in {dir_name}")

    # Determine if the simulation is random or deterministic
    if not options.random:
        logger.info(f"Running simulation in random mode: {is_random}")
        np.random.seed(seed=1714)
        random.seed(1714)

    # Determines the size of the map
    map_size_x = options.size
    map_size_y = options.size

    # Determines the simulation duration (in milliseconds)
    simulation_duration = options.time
    
    # Determines the simulation step (in milliseconds)
    simulation_step = options.step

    # Sets the number of devices, timing mode, transmit interval, payload and DR mode
    device_count        = options.devices
    device_count_lora   = int(options.percentage * device_count)
    device_count_lora_e = device_count - device_count_lora
    data_rate_lora      = options.data_rate_lora
    data_rate_lora_e    = options.data_rate_lora_e
    
    # Sets the device parameters
    device_tx_interval   = options.interval       # Determines the transmit time interval (i.e., 1000 milliseconds)
    device_time_mode     = options.time_mode      # Determines the error mode for transmitting devices (i.e., normal, uniform or exponential distribution), using 'max' forces maximum data rate with exponential distribution
    device_tx_payload    = options.payload        # Determines the transmit payload (i.e., 10 bytes)
    device_position_mode = options.position_mode  # Determines the device position mode (i.e., normal or uniform distribution)
    
    # Sets the gateway parameters
    gateway_area_mode    = options.area_mode      # Determines the area mode to assign DRs (i.e., circules with equal distance or equal area)

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
    gateway.set_sf_thresholds(area_mode=gateway_area_mode)

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
                                                    gateway         = gateway, 
                                                    offset_id       = device_count_lora,
                                                    pre_compute_seq = True,
                                                    sim_duration    = simulation_duration)

    # Add devices to simulation
    for device in devices_lora + devices_lora_e:
        simulation_map.add_device(device)

    # Run the simulation
    simulation.run()

    # Save simulation
    # Results.save_simulation(simulation=simulation, save_sim = False, plot_grid = True)

    # Calculate and save metrics for LoRa and LoRa-E to file
    # metrics = Results.get_metrics(simulation)
    # np.save(dir_name + str(device_count) + '_' + str(device_tx_interval) + '_' + str(options.number), metrics)


if __name__ == "__main__":
    # Get the execute parameters
    options = get_options()

    # Create saving directory if it does not exist
    dir_name = SimulatorHelper.create_save_dir(options)

    # Run simulation
    main(options, dir_name)
