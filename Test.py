import numpy as np


import Device
import DeviceHelper
import Map
import Simulation

test = True
if (test == True):
    random_seed = 1
else:
    random_seed = None

def main():
    np.random.seed(seed=random_seed)

    map_size_x = 100
    map_size_y = 100
    
    device_count = 1
    device_time_mode     = "normal"
    device_position_mode = "normal"
    
    device_tx_interval = 1000 # milliseconds
    device_tx_rate     = 100 # bits/second
    device_tx_payload  = 10 # bytes

    simulation_duration = 6000 # milliseconds
    simulation_step     = 1 # miliseconds
    simulation_channels = 1 # channel
    
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