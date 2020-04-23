import logging

import matplotlib.pyplot as plt

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)


def view_collisions(simulation, device_modulation=None):
    per = get_per(simulation, device_modulation)
    n_devices = len(simulation.simulation_map.get_devices())

    fig = plt.figure()
    plt.title(f'Superimposed Frames. Devices = {n_devices}. PER = {round(per,2)}')
    plt.imshow(simulation.simulation_array, aspect='auto')
    plt.set_cmap('binary')
    plt.colorbar()
    plt.xlabel('Time [ms]')
    plt.ylabel('Frequency [500 Hz channels]')
    fig.savefig('./results/grid.png', format='png', dpi=200)


def get_per(simulation, device_modulation):
    if device_modulation:
        devices = simulation.simulation_map.get_devices()

        # Count collisions
        num_pkt_sent_node = []
        num_pkt_coll_node = []
        for device in devices:
            num_pkt_sent_node.append(device.get_num_frames())
            count = 0
            for pkt in device.pkt_list:
                if pkt.collided:
                    count += 1
            num_pkt_coll_node.append(count)

        return sum(num_pkt_coll_node) / sum(num_pkt_sent_node)
