import numpy as np


# Transmit a frame
def transmit(frames, grid, devices):
    """
    Given a list of frames. Allocate them in time and frequency space.

    :param devices: list of devices in Simulation
    :param frames: The list of frames to allocate in freq and time
    :param grid: The simulation array of size [freq, time],
                    - 0 : the slot is free (not occupied by another frame)
                    - -1 : the slot have been occupied by two or more frames
                    - str : the slot have been occupied by frame with str='owner.number.part'
                            (so this frame can be marked as collided when trying to place another above it)
    :return:
    """

    for frame in frames:
        # Get where to place
        freq, start, end = frame.channel, frame.start_time, frame.end_time
        if frame.channel < 0:
            freq = range(grid.shape[0])  # frame modulation uses all the bandwidth

        # Check for a collision first
        collided = check_collision(devices, grid, frame, freq, start, end)

        # Place within grid
        if collided:
            frame_trace = -1
        else:
            # If no collision, frame should be placed with some information to trace it back, so when
            # a collision happens later in simulation this frame can be marked as collision
            # frame_trace = frame.owner + 1   # to identify packets by owner in grid plot
            # frame_trace = grid[freq, frame.start_time:frame.end_time] + 1
            # frame_trace = -1
            frame_trace = str(frame.owner) + '.' + str(frame.number) + '.' + str(frame.part_num)
        grid[freq, frame.start_time:frame.end_time] = frame_trace


def check_collision(devices, grid, frame, freq, start, end):
    """

    :param devices:
    :param grid:
    :param frame:
    :param freq:
    :param start:
    :param end:
    :return:

    TODO:
        + Define a minimum frame overlap in Time domain to consider a collision
        + Define a minimum frame overlap in Frequency domain to consider a collision (needs clock drift simulation)
    """
    is_one_slot_occupied = np.any(grid[freq, start:end])
    if is_one_slot_occupied:
        # Set this frame as collided
        frame.collided = 1

        # Set the other as collided
        # Get traceability of frames in slots
        bool_list_is_str = [isinstance(value, str) for value in grid[freq, start:end]]
        str_list_frames = grid[freq, start:end][bool_list_is_str]

        # Check if the other frame was not set as collided yet
        if len(str_list_frames) > 0:
            # There will be more than one slot occupied by same frame and can be more than one frame
            str_list_frames_to_trace = np.unique(str_list_frames)

            for frame_trace in str_list_frames_to_trace:
                owner, number, part = frame_trace.split('.')

                # Get list of frames txed by device
                device_frame_list = devices[int(owner)].pkt_list

                # Look up for the first frame that matches the id
                # NOTE: pkt number can be repeated bc it is split into several when FHSS
                # TODO: efficient implementation
                found_it = False
                frame_index = -1
                for frame_index in range(len(device_frame_list)):
                    this_frame = device_frame_list[frame_index]
                    if this_frame.number == int(number):
                        found_it = True
                        break
                assert found_it

                # Set the corresponding part to collided
                device_frame_list[frame_index + int(part)].collided = 1

    else:
        frame.collided = 0
    return is_one_slot_occupied
