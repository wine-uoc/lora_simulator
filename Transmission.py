import numpy as np


# Transmit a frame
def transmit(frames, grid):
    """
    Given a list of frames. Allocate them in time and frequency space.

    :param frames: The list of frames to allocate in freq and time
    :param grid: The simulation array of size [freq, time],
                    - 0 : the slot is free (not occupied by another frame)
                    - -1 : the slot have been occupied by two or more frames
                    - dID > 0 : the slot have been occupied by one frame with id = dID
                                (so this frame can be marked as collided when trying to place another above it)
    :return:
    """

    for frame in frames:
        # Get where to place
        freq, start, end = frame.channel, frame.start_time, frame.end_time
        if frame.channel < 0:
            freq = range(grid.shape[0])  # frame modulation uses all the bandwidth

        # Check for a collision first
        collided = check_collision(grid, frame, freq, start, end)

        # Place within grid
        if collided:
            frame_trace = -1
        else:
            # TODO: if no collision, frame should be placed with some information to trace it back, so when
            #       a collision happens later in simulation this frame can be marked as collision
            # frame_trace = frame.owner + 1   # to identify packets by owner in grid plot
            # frame_trace = grid[freq, frame.start_time:frame.end_time] + 1
            # frame_trace = {'owner': frame.owner, 'id': frame.number, 'part': frame.part_num}
            frame_trace = str(frame.owner) + '.' + str(frame.number) + '.' + str(frame.part_num)
            frame_trace = -1
        grid[freq, frame.start_time:frame.end_time] = frame_trace


def check_collision(grid, frame, freq, start, end):
    """

    :param grid:
    :param frame:
    :param freq:
    :param start:
    :param end:
    :return:

    TODO:
        + Define a minimum frame overlap in Time domain to consider a collision
        + Define a minimum frame overlap in Frequency domain to consider a collision (needs clock drift simulation)
        + The 'first' frame that was placed within the grid should be marked as collided, use frame traceability
    """
    is_one_slot_occupied = np.any(grid[freq, start:end])
    if is_one_slot_occupied:
        frame.collided = 1
    else:
        frame.collided = 0
    pass
    return is_one_slot_occupied
