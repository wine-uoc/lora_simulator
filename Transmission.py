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
            freq = range(grid.shape[0])     # frame modulation uses all the bandwidth

        # Check for a collision first
        check_collision(grid, frame, freq, start, end)

        # Place
        # frame_trace = frame.owner + 1   # to identify packets by owner in grid plot
        # frame_trace = grid[freq, frame.start_time:frame.end_time] + 1
        # frame_trace = {'owner': frame.owner, 'id': frame.number, 'part': frame.part_num}
        # frame_trace = str(frame.owner) + '.' + str(frame.owner) + '.' + str(frame.owner)
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
        + define a minimum frame overlap in time domain to consider a collision
        + also the other 'first' frame should be marked as collided, find frame with id = dID in array
    """
    if np.any(grid[freq, start:end]):
        frame.collided = 1
    else:
        frame.collided = 0
    pass
