import logging

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import colors

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

def save_simulation(simulation = None, save_sim = False, plot_grid = False):
    """
    Save the grid and devices of simulation for debugging or later grid plots.
    """
    assert(simulation != None)
    
    if (save_sim == True):
        np.save('scripts/plots/grid.npy', simulation.simulation_array.copy())
        np.save('scripts/plots/devices.npy', simulation.simulation_map.get_devices())
    
    if (plot_grid == True):
        # Plot each packet using matplotlib rectangle  
        grid = simulation.simulation_array.copy()
        devices = simulation.simulation_map.get_devices()
        
        fig, ax = plt.subplots(1)

        for device in devices:
            pkts = device.pkt_list
            for pkt in pkts:
                start = pkt.start_time
                end = pkt.end_time
                freq = pkt.channel
                width = end - start

                if freq == -1:
                    height = grid.shape[0]
                    freq = 0
                else:
                    height = 1

                if pkt.collided:
                    color = 'red'
                else:
                    color = 'royalblue'
                    
                rect = patches.Rectangle(
                    (start, freq),
                    width,
                    height,
                    linewidth=1,
                    linestyle="-",
                    edgecolor=color,
                    facecolor=color,
                    fill=True,
                    alpha=0.5,
                    antialiased=False,
                )

                ax.add_patch(rect)
        ax.set_title(f'Devices: {len(devices)}')
        ax.set_xlabel('Time (sec)', fontsize=12)
        ax.set_ylabel('Frequency (488 Hz channels)', fontsize=12)
        ax.set_xlim(0, grid.shape[1])
        ax.set_ylim(0, grid.shape[0])
        fig.savefig('./images/simulated_grid.png', format='png', dpi=200)
