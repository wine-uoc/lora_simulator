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
    plt.set_cmap('binary_r')
    plt.colorbar()
    plt.xlabel('Time [ms]')
    plt.ylabel('Frequency [500 Hz channels]')
    fig.savefig('./results/grid.png', format='png', dpi=200)


def get_per(simulation, device_modulation):
    devices = simulation.simulation_map.get_devices()

    # TODO: pass CR as a simulation parameter
    CR = 1/3
    if CR and device_modulation == 'FHSS':
        # TODO: check if correct
        processed_frames_device = []
        collisions_device = []
        for device in devices:
            frame_count = device.get_num_frames()
            processed_frames = 0
            collisions = 0

            for frame_index in range(frame_count):
                this_frame = device.pkt_list[frame_index]
                if frame_index == 0:
                    assert this_frame.is_header     # first frame in list must be a header

                # De-hop the frame to its original form
                total_num_parts = this_frame.n_parts
                header_repetitions = this_frame.num_header
                parts_to_evaluate = device.pkt_list[frame_index:total_num_parts]

                # At least I need one header not collided
                header_decoded = False
                for header_index in range(header_repetitions):
                    this_frame = device.pkt_list[header_index]
                    if not this_frame.collided:
                        header_decoded = True

                if header_decoded:
                    # Maximum parts collided allowed
                    collided_parts_to_notdecode = total_num_parts - int(total_num_parts * CR)

                    # Check how many are
                    collided_count = 0
                    for part in parts_to_evaluate:
                        collided_count = collided_count + part.collided
                    if collided_count > collided_parts_to_notdecode:
                        full_frame_collided = True
                    else:
                        full_frame_collided = False
                else:
                    full_frame_collided = True

                frame_index = frame_index + total_num_parts + 1     # to check if correct
                processed_frames = processed_frames + 1
                if full_frame_collided:
                    collisions = collisions + 1

            processed_frames_device.append(processed_frames)
            collisions_device.append(collisions)

        return sum(collisions_device) / sum(processed_frames_device)

    else:
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
