import numpy as np


# Transmit a frame
def transmit(frames, grid, devices):
    """
    Given a list of frames. Allocate them in time and frequency space.

    :param devices: list of devices in Simulation
    :param frames: The list of frames to allocate in freq and time
    :param grid: The simulation array of size [freq, time],
                    - 0 : the slot is free (not occupied by another frame)
                    - -1 : the slot is occupied by an already collided frames
                    - str : the slot is occupied by frame with str='owner.number.part'
                            (so this frame can be marked as collided when trying to place another above it)
    :return:
    """

    for frame in frames:
        # Get where to place
        freq, start, end = frame.channel, frame.start_time, frame.end_time
        if frame.modulation == 'CSS':
            # Broadband transmission, modulation uses all BW of the channel
            freq = range(grid.shape[0])     

        # Check for a collision first
        collided = check_collision(devices, grid, frame, freq, start, end)

        # Place within grid
        if collided:
            # TODO: as a tuple(0/1, x, x, x)
            frame_trace = -1
        else:
            # If no collision, frame should be placed with some information to trace it back, so 
            # this frame can be marked as collided when a collision happens later in simulation
            # TODO: as a tuple(0/1, x, x, x)
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
        + Define a minimum frame overlap in Frequency domain to consider a collision (needs freq resolution)
    """
    flattened_target_grid = grid[freq, start:end].reshape(-1)
    is_one_slot_occupied = np.any(flattened_target_grid)
    if is_one_slot_occupied:
        # Set this frame as collided
        frame.collided = 1

        # Set the other as collided (only interested in slots containing a string)
        # Get traceability of frames in slots
        bool_list_is_str = [isinstance(value, str) for value in flattened_target_grid]
        str_list_frames = flattened_target_grid[bool_list_is_str]

        # Only if the other frame was not set as collided yet
        if len(str_list_frames) > 0:
            # There can be more than one slot occupied by same frame and can be more than one frame
            str_list_frames_to_trace = np.unique(str_list_frames)

            for frame_trace in str_list_frames_to_trace:
                owner, number, part = frame_trace.split('.')

                # Get list of frames txed by device
                device_frame_list = devices[int(owner)].pkt_list

                # Look up for the first frame that matches the id
                # NOTE: pkt number can be repeated because it was split into several (FHSS)
                frame_index = None
                for i, frame in enumerate(device_frame_list):
                    if frame.number == int(number):
                        frame_index = i
                        break
                # must be somewhere
                assert frame_index is not None      

                # Set the corresponding PART to collided
                device_frame_list[frame_index + int(part)].collided = 1
                
                # Set the frame collided to -1 in grid
                if frame.modulation == 'CSS':
                    # frame occupies all channels
                    freq = range(grid.shape[0]) 
                elif frame.modulation == 'FHSS':
                    # occupies same channel than the other frame
                    grid[freq, frame.start_time:frame.end_time] = -1

    else:
        frame.collided = 0
    return is_one_slot_occupied
