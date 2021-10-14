import argparse
import yaml
import logging
import os
import random
import sys
import numpy as np
from Simulation import Simulation

logger       = logging.getLogger(__name__)
logging_mode = logging.DEBUG #Set logging_mode to INFO to see log info. Set it to DEBUG to see times of execution.
config = yaml.load(open('Simulator.yaml'), Loader=yaml.Loader)

def save_results(dir_name, options, sim, metrics):

    np.save(dir_name + str(options.devices_lora) + '_' +
                        str(options.devices_lora_e) + '_' +
                        str(options.percentage) + '_' +
                        str(options.data_rate_lora) + '_' +
                        str(options.data_rate_lora_e) + '_' +
                        str(options.payload) + '_' +
                        str(options.run_number) + '_' +
                        '.npy', metrics)


def create_save_dir(options):
    """Create a directory to save the results

    Args:
        options (Namespace): Namespace object with values for each argument passed to the script

    Returns:
        str: Directory name string
    """
    if options.use_ratios == 0:
        if options.data_rate_set_1 in range(0,6):
            set_1_dirname = 'CSS'
        else:
            set_1_dirname = 'FHSS'
        if options.data_rate_set_2 in range(0,6):
            set_2_dirname = 'CSS'
        else:
            set_2_dirname = 'FHSS'
        dir_name = f'{config["common"]["root_dir_name"]}/DR_{options.data_rate_set_1}/DR_{options.data_rate_set_2}/pl_{options.payload}/{set_1_dirname}_{options.devices_set_1}/{set_2_dirname}_{options.devices_set_2}'
    else:
        dir_name = f'{config["common"]["root_dir_name"]}/DR_{options.data_rate_set_1}/DR_{options.data_rate_set_2}/pl_{options.payload}/ratio_{options.lora_ratio}/{options.num_devices}_devices'


    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        
    return dir_name

def get_options(args=None):
    """Parse input arguments

    Args:
        args ([str], optional): list of arguments. Defaults to None.

    Returns:
        Namespace: object holding parsed arguments
    """
    # If we don't pass argument list, get from standard input
    if args is None:
        args = sys.argv[1:]

    # Create parameter parser
    parser = argparse.ArgumentParser(description="WiNe Simulator for LoRa/LoRa_E networks.")

    # Add parameters to parser
    parser.add_argument("-s", "--size", type=int, default=1378822, help="Size of each simulation area side (i.e., x and y) in meters.")
    parser.add_argument("-d1", "--devices_set_1", type=int, default=100, help="Number of devices for the first set in the simulation.")
    parser.add_argument("-d2", "--devices_set_2", type=int, default=100, help="Number of devices for the second set in the simulation.")
    parser.add_argument("-t", "--time", type=int, default=3600000, help="Duration of the simulation in milliseconds.")
    parser.add_argument("-st", "--step", type=int, default=1, help="Time step of the simulation in milliseconds.")
    parser.add_argument("-i", "--interval", type=int, default=10000, help="Transmit interval for each device (ms).")
    parser.add_argument("-n", "--run_number", type=int, default=0, help="Number of script run (for file naming purposes).")
    parser.add_argument("-pm", "--position_mode", type=str, default='annulus', choices=['annulus', 'normal', 'uniform'] ,help="Node positioning mode (i.e., normal distribution or uniform distribution).")
    parser.add_argument("-pmv", "--position_mode_values", type=float, default=[180, 190], nargs='*', help="inner radius and outer radius values for annulus position mode, std for normal position mode" )
    parser.add_argument("-tm", "--time_mode", type=str, default='expo', choices=['deterministic', 'normal', 'uniform', 'expo', 'naive'] , help="Time error mode for transmitting devices")
    parser.add_argument("-pl", "--payload", type=int, default=10, help="Transmit payload of each device (bytes).")
    parser.add_argument("-l", "--logging_file", type=str, default='Simulator.log', help="Name of the logging filename.") #TODO: delete?
    parser.add_argument("-r", "--random", type=int, default=1, choices=[0, 1], help="Determines if the simulation is random or deterministic (i.e., True is random).")
    parser.add_argument("-dr1", "--data_rate_set_1", type=int, default=1, choices=[0,1,2,3,4,5,8,9], help="Data rate mode for devices in set 1. When use_ratios=1, valid values are [0-5]")
    parser.add_argument("-dr2", "--data_rate_set_2", type=int, default=1, choices=[0,1,2,3,4,5,8,9], help="Data rate mode for devices in set 2. When use_ratios=1, valid values are [8-9]")
    parser.add_argument("-pwr", "--tx_power", type=int, default=14, help="TX power of the devices (dBm).")
    parser.add_argument("-auto", "--auto_data_rate_lora", type=int, default=0, choices=[0, 1], help="Determines whether LoRa data rate mode selection is automatic or not") 
    parser.add_argument("-ur", "--use_ratios", type=int, default=0, help="Enables simulation using LoRa devices ratio instead of fixed numbers of LoRa/LoRa-E devices.")
    parser.add_argument("-lr", "--lora_ratio", type=float, default=0, help="Ratio of LoRa devices in the simulation. Used when use_ratios=1.")
    parser.add_argument("-d", "--num_devices", type=int, default=0, help="Number of total devices to simulate. Used when use_ratios=1")
    parser.add_argument("-tha", "--lora_packet_loss_threshold", type=float, default=0.0, help="LoRa packet loss threshold.") #TODO: delete?
    parser.add_argument("-the", "--lora_e_packet_loss_threshold", type=float, default=0.0, help="LoRa-E packet loss threshold.") #TODO: delete?
    parser.add_argument("-ss", "--save_simulation", type=int, default=0, help="Saves grid in a PNG file.") #TODO: delete?

    # Parse arguments
    options = parser.parse_args(args)

    if options.position_mode == 'annulus' and len(options.position_mode_values) != 2:
        parser.error("position_mode=annulus requires 2 arguments for position_mode_values!")
    elif options.position_mode == 'normal' and len(options.position_mode_values) != 1:
        parser.error("position_mode=normal requires only 1 argument for position_mode_values!")
    elif options.use_ratios == 1:
        if options.data_rate_set_1 not in range(0,6):
            parser.error("When use_ratios=1, data_rate_set_1=[0-5]!")
        elif options.data_rate_set_2 not in range(8,10):
            parser.error("When use_ratios=1, data_rate_set_2=[8-9]!")


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
        logger.info(f"Running simulation in random mode: {False}")
        np.random.seed(seed=1714)
        random.seed(1714)

    sim = Simulation(
        options.size, options.devices_set_1, options.devices_set_2, 
        options.time, options.step, options.interval, options.run_number,
        options.position_mode, options.position_mode_values, options.time_mode,
        options.payload, options.use_ratios, options.lora_ratio, options.num_devices,
        options.data_rate_set_1, options.data_rate_set_2, options.auto_data_rate_lora,
        options.tx_power, options.lora_packet_loss_threshold, 
        options.lora_e_packet_loss_threshold,
        options.save_simulation, dir_name
    )

    sim.run()

    metrics = sim.get_metrics()
    logger.info(f'metrics: {metrics}')

    #save_results(dir_name, options, sim, metrics)

if __name__ == "__main__":
    # Get the execute parameters
    options = get_options()

    # Create saving directory if it does not exist
    dir_name = create_save_dir(options)

    # Check if simulation is duplicated
    if not os.path.exists(f'{dir_name}/r_{options.run_number}_.csv'):
        main(options, dir_name)
    else:
        print('Simulation had already been performed! Skipping...')
