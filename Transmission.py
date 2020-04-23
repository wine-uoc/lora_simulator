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
                                (so this frame can be marked as collided)
    :return:
    """

    if len(frames) > 1:
        # Do frequency hopping, place each frame to corresponding freq and time
        for frame in frames:
            # Get where to place
            freq, start, end = frame.channel, frame.start_time, frame.end_time

            # Check for a collision first
            check_collision(grid, frame, freq, start, end)

            # Place
            frame_trace = -1
            frame_trace = frame.owner + 1   # to identify packets by owner in grid plot
            grid[freq, frame.start_time:frame.end_time] = frame_trace
    else:
        # Frame was not divided in freq
        frame = frames[0]

        # First, check collision only in time domain
        # TODO: define a minimun frame overlap in time domain to consider a collision
        if np.any(grid[:, frame.start_time:frame.end_time]):    # collision at some point
            frame.collided = 1
            # TODO: also the other 'first' frame should be marked as collided, find frame with id = dID in array
        else:
            frame.collided = 0

        # Fill frequency and time slots, transmit using all the spectrum
        # frame_trace = grid[:, frame.start_time:frame.end_time] + 1
        # frame_trace = {'owner': frame.owner, 'id': frame.number, 'part': frame.part_num}
        # frame_trace = str(frame.owner) + '.' + str(frame.owner) + '.' + str(frame.owner)
        frame_trace = -1
        grid[:, frame.start_time:frame.end_time] = frame_trace


def check_collision(grid, frame, freq, start, end):
    # TODO same above
    if np.any(grid[freq, start:end]):  # collision at some point
        frame.collided = 1
    else:
        frame.collided = 0
    pass
