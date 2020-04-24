import logging

import matplotlib.pyplot as plt
import numpy as np

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)


def view_collisions(simulation, device_modulation=None):
    per = get_per(simulation, device_modulation)
    n_devices = len(simulation.simulation_map.get_devices())

    # Workaround if array is of type object
    grid = simulation.simulation_array
    grid = grid != 0

    fig = plt.figure()
    plt.title(f'Superimposed Frames. Devices = {n_devices}. PER = {round(per,2)}')
    plt.imshow(grid, aspect='auto')
    plt.set_cmap('binary')
    plt.colorbar()
    plt.xlabel('Time [ms]')
    plt.ylabel('Frequency [500 Hz channels]')
    fig.savefig('./results/grid.png', format='png', dpi=200)


def get_per(simulation, device_modulation):
    """
    Compute Packet Error Rate given Simulation class with frames transmitted associated to each device.
    If modulation is FHSS, apply CR in PER calculation.

    :param simulation: simulation class
    :param device_modulation: modulation type
    :return: Packet Error Rate
    """
    devices = simulation.simulation_map.get_devices()

    # TODO: pass CR as a simulation parameter
    CR = 1/3
    if CR and device_modulation == 'FHSS':
        # TODO: check if correct
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
                    assert this_frame.is_header     # sanity check: first frame in list must be a header

                # De-hop the frame to its original form
                total_num_parts = this_frame.n_parts
                header_repetitions = this_frame.num_header
                headers_to_evaluate = device.pkt_list[frame_index:frame_index+header_repetitions]
                num_payloads = total_num_parts - header_repetitions
                pls_to_evaluate = device.pkt_list[frame_index+header_repetitions:frame_index+total_num_parts]

                # At least I need one header not collided
                header_decoded = False
                for header in headers_to_evaluate:
                    assert header.is_header         # sanity check
                    if not header.collided:
                        header_decoded = True

                if header_decoded:
                    # Maximum payloads collided allowed
                    collided_pls_to_not_decode = num_payloads - int(np.ceil(num_payloads * CR))

                    # Check how many collided
                    collided_pls_count = 0
                    for pl in pls_to_evaluate:
                        assert not pl.is_header     # sanity check
                        collided_pls_count = collided_pls_count + pl.collided
                    if collided_pls_count > collided_pls_to_not_decode:
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
