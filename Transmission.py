import numpy as np

# Transmit a frame
def transmit(frames, sim_grid, devices):
    """
    Given a list of frames. Allocate them in time and frequency space.

    :param devices:  List of devices in Simulation
    :param frames:   List of frames to allocate in freq and time
    :param sim_grid: Simulation array of size [freq, time]
                     Contains a tuple(int32, uint32, uint32) corresponding to (frame.owner, frame.number, frame.part_num)
                     The frame.owner can take the following values:
                      -  0      : the slot is free (not occupied by another frame)
                      - -1      : the slot is occupied by an already collided frames
                      - node_id : the slot is occupied by frame with frame.owner
                            (so this frame can be marked as collided when trying to place another above it)
    :return:
    """

    for frame in frames:
        # Get where to place
        freq, start, end = (frame.channel, frame.start_time, frame.end_time)

        if frame.modulation == 'CSS':
            # Broadband transmission, modulation uses all BW of the channel
            freq = range(sim_grid.shape[0])     

        # Check for a collision first
        collided = check_collision(devices, sim_grid, frame, freq, start, end)

        # Place within the grid
        if (collided == True):
            frame_trace = (-1, 0, 0)
        else:
            # If no collision, frame should be placed with some information to trace it back, so 
            # this frame can be marked as collided when a collision happens later in simulation
            frame_trace = (frame.owner, frame.number, frame.part_num)

        # Place the frame in the grid
        sim_grid[freq, frame.start_time:frame.end_time] = frame_trace


def check_collision(devices, sim_grid, frame, freq, start, end):
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
    # Create a grid view that covers only the area of interest of the frame (i.e., frequency and time)
    sim_grid_nodes  = sim_grid[freq, start:end, 0]
    
    # Check if at least one of the slots in the grid view is being used
    is_one_slot_occupied = np.any(np.where(sim_grid_nodes != 0))
    
    # If at least one slot in the grid is occupied
    if is_one_slot_occupied:
        # Mark this frame as collided
        frame.collided = True

        # Search the frames that have collided inside the grid view
        # Cells in the matrix can have the following values:
        # -1 if they have already COLLIDED
        #  0 if they are currently EMPTY
        # >0 if they are currently SUCCESSFUL
        collided_index = np.argwhere(sim_grid_nodes > 0)
        
        # If we have found collided frames
        if (len(collided_index > 0)):
            # Get the nodes, frames and subframes view from the sim_grid
            scratch_nodes     = sim_grid[freq, start:end, 0]
            scratch_frames    = sim_grid[freq, start:end, 1]
            scratch_subframes = sim_grid[freq, start:end, 2]
            
            # When FHSS the resulting collioded_index will be a row with the collision positions
            if (frame.modulation == "FHSS"):
                print("FHSS {}".format(collided_index.shape))
                for i in collided_index:
                    x = scratch_nodes[i]
                    assert(x > 0)
            
            # When CSS the resulting collided_index will be a 2D matrix with the collisions positions
            elif (frame.modulation == "CSS"):
                print("CSS {}".format(collided_index.shape))
                for index in collided_index:
                    i, j = index
                    x = scratch_nodes[i, j]
                    assert(x > 0)
                


    else:
        frame.collided = False
    
    return False
