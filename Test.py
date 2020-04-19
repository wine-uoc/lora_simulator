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
    
    device_count = 1000
    device_distribution_mode = "normal"

    simulation_time = 1000
    simulation_step = 0.1
    
    simulation_map = Map.Map(x=map_size_x, y=map_size_y)

    simulation = Simulation.Simulation(time=simulation_time, step=simulation_step, map=simulation_map)
    simulation.run()

    for i in range(device_count):
        d = Device.Device(id=i, mode=device_distribution_mode, max_x=map_size_x , max_y=map_size_y)
        simulation_map.add_device(d)
    
    DeviceHelper.DeviceHelper.plot_device_position(device_list=simulation_map.get_devices(), map_size=(map_size_x, map_size_y))

if __name__ == "__main__":
    main()