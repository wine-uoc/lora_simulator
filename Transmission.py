import numpy as np


# Transmit a packet
def transmit(packet, sim_grid):

    # start_time = 1
    # duration = 50
    # end_time = start_time + duration
    # import Packet
    # packet = Packet.Packet(1, 1, 1, 'fhss')
    # array = np.zeros((10, 100))

    if packet.modulation == 'fhss':
        # Do frequency hopping

        # frame partition
        # place them within the grid
        # check if other present

        pass
    else:
        # Check collision
        # TODO: define a minimun packet overlap in time domain
        if np.any(sim_grid[:, packet.start_time:packet.end_time]):    # collision at some point
            packet.collided = 1
        else:
            packet.collided = 0
        # Transmit using all the spectrum anyway
        sim_grid[:, packet.start_time:packet.end_time] = sim_grid[:, packet.start_time:packet.end_time] + 1


def check_collision():
    pass
