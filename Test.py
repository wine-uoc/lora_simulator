import configparser
import logging

import numpy as np

import Device
import DeviceHelper
import Map
import Simulation

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('Test.cfg')

def main():
    logging.basicConfig(level=logging.DEBUG, filename='Test.log', filemode='w', format='%(filename)s:%(lineno)s %(levelname)s: %(message)s')

    # Determines if the simulation is random or deterministic
    is_random = config.getboolean('simulation', 'is_random')
    if (is_random == False):
        logger.info("Running simulation in random mode: {}".format(is_random))
        np.random.seed(seed=None)

    map_size_x = config.getint('simulation', 'map_size_x')
    map_size_y = config.getint('simulation', 'map_size_y')
    
    device_time_mode     = config.get('simulation', 'device_time_mode')
    device_position_mode = config.get('simulation', 'device_position_mode')
    
    device_count       = config.getint('simulation', 'device_count')
    device_tx_interval = config.getint('simulation', 'device_tx_interval')
    device_tx_rate     = config.getint('simulation', 'device_tx_rate')
    device_tx_payload  = config.getint('simulation', 'device_tx_payload')

    simulation_duration = config.getint('simulation', 'simulation_duration')
    simulation_step     = config.getint('simulation', 'simulation_step')
    simulation_channels = config.getint('simulation', 'simulation_channels')
    
    # Create the simulation map
    simulation_map = Map.Map(x=map_size_x, y=map_size_y)

    # Create the simulation
    simulation = Simulation.Simulation(simulation_duration=simulation_duration, simulation_step=simulation_step,
                                       simulation_channels=simulation_channels, simulation_map=simulation_map)

    # Create the devices and add them to the simulation
    for device_id in range(device_count):
        device = Device.Device(device_id=device_id, time_mode=device_time_mode, position_mode=device_position_mode, max_x=map_size_x, max_y=map_size_y, 
                               tx_interval=device_tx_interval, tx_rate=device_tx_rate, tx_payload=device_tx_payload)
        simulation_map.add_device(device)
    
    # Run the simulation
    simulation.run()

if __name__ == "__main__":
    main()