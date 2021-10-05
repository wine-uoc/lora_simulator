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
    dir_name = f'{config["common"]["root_dir_name"]}/DR_{options.data_rate_lora}/DR_{options.data_rate_lora_e}/pl_{options.payload}/CSS_{options.devices_lora}/FHSS_{options.devices_lora_e}'

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
    parser.add_argument("-da", "--devices_lora", type=int, default=50, help="Number of LoRa devices in the simulation.")
    parser.add_argument("-de", "--devices_lora_e", type=int, default=0, help="Number of LoRa-E devices in the simulation.")
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
    parser.add_argument("-p", "--percentage", type=float, default=0.5, help="Percentage of LoRa devices with respect to LoRa-E (i.e., 1.0 is all LoRa devices).") #TODO: delete?
    parser.add_argument("-dra", "--data_rate_lora", type=int, default=1, choices=range(0,6) ,help="LoRa data rate mode.")
    parser.add_argument("-dre", "--data_rate_lora_e", type=int, default=8, choices=[8, 9], help="LoRa-E data rate mode.")
    parser.add_argument("-pwr", "--tx_power", type=int, default=14, help="TX power of the devices (dBm).")
    parser.add_argument("-auto", "--auto_data_rate_lora", type=int, default=0, choices=[0, 1], help="Determines whether LoRa data rate mode selection is automatic or not") 
    parser.add_argument("-tha", "--lora_packet_loss_threshold", type=float, default=0.0, help="LoRa packet loss threshold.") #TODO: delete?
    parser.add_argument("-the", "--lora_e_packet_loss_threshold", type=float, default=0.0, help="LoRa-E packet loss threshold.") #TODO: delete?
    parser.add_argument("-ss", "--save_simulation", type=int, default=0, help="Saves grid in a PNG file.") #TODO: delete?

    # Parse arguments
    options = parser.parse_args(args)

    if ((options.position_mode == 'annulus' and len(options.position_mode_values) != 2) or \
        (options.position_mode == 'normal' and len(options.position_mode_values) != 1)):
        print("Argument values are wrong!")
        exit(-1)

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
        options.size, options.devices_lora, options.devices_lora_e, 
        options.time, options.step, options.interval, options.run_number,
        options.position_mode, options.position_mode_values, options.time_mode,
        options.payload, options.percentage, options.data_rate_lora,
        options.data_rate_lora_e, options.auto_data_rate_lora,
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
