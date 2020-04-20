import numpy as np


# Transmit a frame
def transmit(frame, sim_grid):

    # start_time = 1
    # duration = 50
    # end_time = start_time + duration
    # import frame
    # frame = frame.frame(1, 1, 1, 'fhss')
    # array = np.zeros((10, 100))

    if frame.modulation == 'fhss':
        # Do frequency hopping

        # frame partition into n hops
        # place them within the grid
        # check for collisions
        # TODO: thing how frames are represented in the array to allow frame traceability

        pass
    else:
        # Check collision only in time domain
        # TODO: define a minimun frame overlap in time domain
        if np.any(sim_grid[:, frame.start_time:frame.end_time]):    # collision at some point
            frame.collided = 1
            # TODO: also the other frame should be marked as collided
        else:
            frame.collided = 0
        # Transmit using all the spectrum anyway
        sim_grid[:, frame.start_time:frame.end_time] = sim_grid[:, frame.start_time:frame.end_time] + 1


def check_collision():
    pass
