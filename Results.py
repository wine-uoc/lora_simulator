import logging

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)


def view_collisions(simulation, device_modulation=None, coding_rate=None):
    #per = get_per(simulation, device_modulation, coding_rate)
    per = 0
    n_devices = len(simulation.simulation_map.get_devices())
    grid = simulation.simulation_array.copy()
    np.save('scripts/plots/grid.npy', grid)
    np.save('scripts/plots/devices.npy', simulation.simulation_map.get_devices())

    # Workaround to plot frames collided and non-collided if array is of type object
    # 2: frame allocated w/o collision, 1: collided frame
    # TODO this approach has some errors, replace by code in script plot_grid
    nr, nc = grid.shape
    grid_reshaped = grid.copy().reshape(-1)
    bool_list_is_str = [isinstance(value, str) for value in grid_reshaped]
    grid_reshaped[bool_list_is_str] = 2
    grid = grid_reshaped.reshape(nr, nc).copy()
    del grid_reshaped
    grid = abs(grid.astype(np.int8))    # -1 to 1

    cmap = colors.ListedColormap(['white', 'red', 'k'])
    bounds = [0, 1, 2, 3]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig = plt.figure()
    plt.title(f'Superimposed Frames. Devices = {n_devices}. PDR = {round(1 - per, 2)}')
    img = plt.imshow(grid, origin="lower", aspect='auto', interpolation='nearest', cmap=cmap, norm=norm)
    # plt.set_cmap('binary')
    # plt.colorbar(img, ticks=[0, 1, 2])
    plt.xlabel('Time [ms]')
    plt.ylabel('Frequency [488 Hz channels]')
    fig.savefig('./results/grid.png', format='png', dpi=200)

    # Let create a semi-transparent frames plot, to see overlapping
    if device_modulation != 'FHSS':
        fig, ax = plt.subplots(1)
        ax.plot(0, grid.shape[1])
        ax.plot(grid.shape[1], 0)
        dvs = simulation.simulation_map.get_devices()
        for device in dvs:
            pkts = device.pkt_list
            for pkt in pkts:
                start = pkt.start_time
                end = pkt.end_time
                height = grid.shape[1]
                width = end - start
                if pkt.collided:
                    color = 'red'
                else:
                    color = 'k'
                rect = patches.Rectangle((start, 0), width, height, linewidth=1, edgecolor='k', facecolor=color, fill=True, alpha=0.5)
                ax.add_patch(rect)

        fig.savefig('./results/grid_2.png', format='png', dpi=200)


def get_per(simulation, device_modulation, numerator_coding_rate=None):
    """
    Compute Packet Error Rate given Simulation class with frames transmitted associated to each device.
    If modulation is FHSS, apply CR in PER calculation.

    :param CR:
    :param simulation: simulation class
    :param device_modulation: modulation type
    :return: Packet Error Rate
    """
    devices = simulation.simulation_map.get_devices()
    CR = numerator_coding_rate / 3

    if CR and device_modulation == 'FHSS':
        de_hopped_frames_device = []
        collisions_device = []

        # Count collisions for each device in simulation
        for device in devices:
            frame_count = device.get_num_frames()
            de_hopped_frames_count = 0
            collisions_count = 0

            # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided
            frame_index = 0
            while frame_index < frame_count:
                this_frame = device.pkt_list[frame_index]
                if frame_index == 0:
                    assert this_frame.is_header  # sanity check: first frame in list must be a header

                # De-hop the frame to its original form
                total_num_parts = this_frame.n_parts
                header_repetitions = this_frame.num_header
                headers_to_evaluate = device.pkt_list[frame_index:frame_index + header_repetitions]
                pls_to_evaluate = device.pkt_list[frame_index + header_repetitions:frame_index + total_num_parts]

                # At least I need one header not collided
                header_decoded = False
                for header in headers_to_evaluate:
                    assert header.is_header  # sanity check
                    if not header.collided:
                        header_decoded = True
                        break

                if header_decoded:
                    # Check how many pls collided
                    collided_pls_time_count = 0
                    non_collided_pls_time_count = 0
                    for pl in pls_to_evaluate:
                        assert not pl.is_header  # sanity check
                        if pl.collided:
                            collided_pls_time_count = collided_pls_time_count + pl.duration
                        else:
                            non_collided_pls_time_count = non_collided_pls_time_count + pl.duration

                    # Check for time ratio, equivalent to bit
                    calc_cr = non_collided_pls_time_count / (non_collided_pls_time_count + collided_pls_time_count)
                    if calc_cr < CR:
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
            de_hopped_frames_device.append(de_hopped_frames_count)
            collisions_device.append(collisions_count)

            # Sanity check: de-hopped frames should be equal to the number of unique frame ids
            pkt_nums = []
            for pkt in device.pkt_list:
                pkt_nums.append(pkt.number)
            assert len(set(pkt_nums)) == de_hopped_frames_count

        # Return PER
        return sum(collisions_device) / sum(de_hopped_frames_device)

    else:
        # Straight-forward collision count
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


def get_num_rxed_gen_node(simulation, device_modulation, numerator_coding_rate=None):
    # Temporary method
    devices = simulation.simulation_map.get_devices()
    CR = numerator_coding_rate / 3

    if CR and device_modulation == 'FHSS':
        de_hopped_frames_device = []
        collisions_device = []

        # Count collisions for each device in simulation
        for device in devices:
            frame_count = device.get_num_frames()
            de_hopped_frames_count = 0
            collisions_count = 0

            # Iterate over frames, de-hop, count whole frame as collision if (1-CR) * num_pls payloads collided
            frame_index = 0
            while frame_index < frame_count:
                this_frame = device.pkt_list[frame_index]
                if frame_index == 0:
                    assert this_frame.is_header  # sanity check: first frame in list must be a header

                # De-hop the frame to its original form
                total_num_parts = this_frame.n_parts
                header_repetitions = this_frame.num_header
                headers_to_evaluate = device.pkt_list[frame_index:frame_index + header_repetitions]
                pls_to_evaluate = device.pkt_list[frame_index + header_repetitions:frame_index + total_num_parts]

                # At least I need one header not collided
                header_decoded = False
                for header in headers_to_evaluate:
                    assert header.is_header  # sanity check
                    if not header.collided:
                        header_decoded = True
                        break

                if header_decoded:
                    # Check how many pls collided
                    collided_pls_time_count = 0
                    non_collided_pls_time_count = 0
                    for pl in pls_to_evaluate:
                        assert not pl.is_header  # sanity check
                        if pl.collided:
                            collided_pls_time_count = collided_pls_time_count + pl.duration
                        else:
                            non_collided_pls_time_count = non_collided_pls_time_count + pl.duration

                    # Check for time ratio, equivalent to bit
                    calc_cr = non_collided_pls_time_count / (non_collided_pls_time_count + collided_pls_time_count)
                    if calc_cr < CR:
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
            de_hopped_frames_device.append(de_hopped_frames_count)
            collisions_device.append(collisions_count)

            # Sanity check: de-hopped frames should be equal to the number of unique frame ids
            pkt_nums = []
            for pkt in device.pkt_list:
                pkt_nums.append(pkt.number)
            assert len(set(pkt_nums)) == de_hopped_frames_count

        # Return
        n_coll_dev = np.mean(collisions_device)
        n_gen_dev = np.mean(de_hopped_frames_device)
        n_rxed_dev = n_gen_dev - n_coll_dev
        return n_rxed_dev, n_gen_dev

    else:
        # Straight-forward collision count
        num_pkt_sent_node = []
        num_pkt_coll_node = []
        for device in devices:
            num_pkt_sent_node.append(device.get_num_frames())
            count = 0
            for pkt in device.pkt_list:
                if pkt.collided:
                    count += 1
            num_pkt_coll_node.append(count)

        n_coll_dev = np.mean(num_pkt_coll_node)
        n_gen_dev = np.mean(num_pkt_sent_node)
        n_rxed_dev = n_gen_dev - n_coll_dev
        # num_pkt_sent_node = []
        # num_pkt_coll_node = []
        # num_pkt_rxed_node = []
        # for device in devices:
        #     num_pkt_sent_node.append(device.get_num_frames())
        #     count_coll = 0
        #     count_rxed = 0
        #     for pkt in device.pkt_list:
        #         if pkt.collided:
        #             count_coll += 1
        #         else:
        #             count_rxed += 1
        #     num_pkt_coll_node.append(count_coll)
        #     num_pkt_rxed_node.append(count_rxed)
        #     assert count_rxed == device.get_num_frames() - count_coll
        #
        # n_coll_dev = sum(num_pkt_coll_node)
        # n_gen_dev = sum(num_pkt_sent_node)
        # n_rxed_dev = sum(num_pkt_rxed_node)
        return n_rxed_dev, n_gen_dev


