import numpy as np


# Transmit a frame
def transmit(frame, sim_grid):

    if frame.modulation == 'FHSS':
        # Do frequency hopping
        total_frame_duration = frame.duration
        part_duration = frame.hop_duration
        last_part_duration = 0

        # frame partition into n hops
        n_parts = int(np.floor(total_frame_duration / float(part_duration)))    # n parts of duration T_hop
        last_part_duration = total_frame_duration % part_duration               # last part duration
        # NOTE: n_parts * part_duration + last_part_duration = total_frame_duration

        # place first parts within the grid
        # check for collisions
        for part in range(n_parts):
            pass

        if last_part_duration:
            # place last part if exists
            pass

        # TODO:
        #  + think how frames are represented in the array to allow frame traceability
        #  + header behaves differently

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
