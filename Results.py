import logging

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)


def save_simulation(simulation, save_sim, plot_grid):
    """
    Save the grid and devices of simulation for debugging or later grid plots.
    """
    if save_sim:
        np.save('scripts/plots/grid.npy', simulation.simulation_array.copy())
        np.save('scripts/plots/devices.npy', simulation.simulation_map.get_devices())
    
    if plot_grid:
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

def get_metrics(simulation):
    """ 
    Returns tuple of size 4 with received and generated packets for LoRa and LoRa-E devices
    """
    devices = simulation.simulation_map.get_devices()

    # LoRa lists
    lora_num_pkt_sent_list = []
    lora_num_pkt_coll_list = []

    # LoRa-E lists
    lora_e_num_pkt_sent_list = []
    lora_e_num_pkt_coll_list = []

    # Count collisions for each device in simulation
    for device in devices:
        
        if device.modulation == 'FHSS':

            frame_count = device.get_num_frames()
            de_hopped_frames_count = 0
            collisions_count = 0

            # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided
            frame_index = 0
            while frame_index < frame_count:
                this_frame = device.pkt_list[frame_index]
                if frame_index == 0:
                    assert this_frame.is_header     # sanity check: first frame in list must be a header

                # De-hop the frame to its original form
                total_num_parts = this_frame.n_parts
                header_repetitions = this_frame.num_header
                headers_to_evaluate = device.pkt_list[frame_index:frame_index + header_repetitions]
                pls_to_evaluate = device.pkt_list[frame_index + header_repetitions:frame_index + total_num_parts]

                # At least I need one header not collided
                header_decoded = False
                for header in headers_to_evaluate:
                    assert header.is_header         # sanity check
                    if not header.collided:
                        header_decoded = True
                        break

                if header_decoded:
                    # Check how many pls collided
                    collided_pls_time_count = 0
                    non_collided_pls_time_count = 0
                    for pl in pls_to_evaluate:
                        assert not pl.is_header     # sanity check
                        if pl.collided:
                            collided_pls_time_count = collided_pls_time_count + pl.duration
                        else:
                            non_collided_pls_time_count = non_collided_pls_time_count + pl.duration

                    # Check for time ratio, equivalent to bit
                    calculated_ratio = float(non_collided_pls_time_count) / (non_collided_pls_time_count + collided_pls_time_count)
                    if calculated_ratio < device.cr:
                        de_hopped_frame_collided = True
                    else:
                        de_hopped_frame_collided = False
                else:
                    de_hopped_frame_collided = True

                # Prepare next iter
                frame_index = frame_index + total_num_parts
                de_hopped_frames_count = de_hopped_frames_count + 1

                # Increase collision count if frame can not be decoded
                if de_hopped_frame_collided:
                    collisions_count = collisions_count + 1

            # Store device results
            lora_e_num_pkt_sent_list.append(de_hopped_frames_count)
            lora_e_num_pkt_coll_list.append(collisions_count)

            # Sanity check: de-hopped frames should be equal to the number of unique frame ids
            pkt_nums = [pkt.number for pkt in device.pkt_list]
            assert len(set(pkt_nums)) == de_hopped_frames_count

        elif device.modulation == 'CSS':
            # Straight-forward collision count
            # how many packets were sent by the device
            lora_num_pkt_sent_list.append(device.get_num_frames())

            # how many of them collided
            count = 0
            for pkt in device.pkt_list:
                if pkt.collided:
                    count += 1
            lora_num_pkt_coll_list.append(count)

    # Calculate LoRa metrics
    if lora_num_pkt_sent_list:
        n_coll_per_dev = np.nanmean(lora_num_pkt_coll_list)
        n_gen_per_dev = np.nanmean(lora_num_pkt_sent_list)
        n_rxed_per_dev = n_gen_per_dev - n_coll_per_dev
    else:
        n_gen_per_dev = None
        n_rxed_per_dev = None

    # Calculate LoRa-E metrics
    if lora_e_num_pkt_sent_list:
        n_coll_per_dev_lora_e = np.nanmean(lora_e_num_pkt_coll_list)
        n_gen_per_dev_lora_e = np.nanmean(lora_e_num_pkt_sent_list)
        n_rxed_per_dev_lora_e = n_gen_per_dev_lora_e - n_coll_per_dev_lora_e
    else:
        n_gen_per_dev_lora_e = None
        n_rxed_per_dev_lora_e = None
    #lora_pdr_network = 1. - sum(lora_num_pkt_coll_list) / sum(lora_num_pkt_sent_list) if lora_num_pkt_sent_list else None
    #lora_e_pdr_network = 1. - sum(lora_e_num_pkt_coll_list) / sum(lora_e_num_pkt_sent_list) if lora_e_num_pkt_sent_list else None

    metrics = (n_rxed_per_dev, n_gen_per_dev, n_rxed_per_dev_lora_e, n_gen_per_dev_lora_e)

    return metrics