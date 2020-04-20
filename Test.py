import configparser
import logging

import numpy as np

import Device
import Map
import Results
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

    device_count       = config.getint('simulation', 'device_count')
    device_tx_interval = config.getint('simulation', 'device_tx_interval')
    device_tx_rate     = config.getint('simulation', 'device_tx_rate')
    device_tx_payload  = config.getint('simulation', 'device_tx_payload')

    device_time_mode     = config.get('simulation', 'device_time_mode')
    device_position_mode = config.get('simulation', 'device_position_mode')

    device_modulation = config.get('simulation', 'device_modulation')
    hop_duration      = config.getint('simulation', 'fhss_hop_duration')

    simulation_duration = config.getint('simulation', 'simulation_duration')
    simulation_step     = config.getint('simulation', 'simulation_step')
    simulation_channels = config.getint('simulation', 'simulation_channels')
    
    # Create the map
    simulation_map = Map.Map(size_x=map_size_x, size_y=map_size_y, position_mode=device_position_mode)

    # Create the simulation
    simulation = Simulation.Simulation(simulation_duration=simulation_duration, simulation_step=simulation_step,
                                       simulation_channels=simulation_channels, simulation_map=simulation_map)

    # Create the devices and add them to the simulation
    for device_id in range(device_count):
        # Create device
        device = Device.Device(device_id=device_id, time_mode=device_time_mode, tx_interval=device_tx_interval,
                               tx_rate=device_tx_rate, tx_payload=device_tx_payload, modulation=device_modulation,
                               hop_duration=hop_duration)
        # Add device to simulation
        simulation_map.add_device(device)
    
    # Run the simulation
    simulation.run()

    # View collisons
    Results.view_collisions(simulation)


if __name__ == "__main__":
    main()
