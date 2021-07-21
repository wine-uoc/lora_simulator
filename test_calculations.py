import numpy as np
import zlib
'''
next_hop_list = [8*i for i in range(0,35)]
for i in range(0,280):
    for hop in next_hop_list:
        res = abs(((hop+i)%280) - i) >= 8
        if res == False:
            print(f'ch_i = {i}, ch_i+1 = {(hop+i)%280}, hop = {hop}')
'''
def my_hash(value):
        """Creates a hash from a value

        Args:
            value (int): value from which to create a hash

        Returns:
            int32: 32-bit hash 
        """
        # Define our int to bytes conversion procedure
        value_bytes = int(value).to_bytes(8, 'big', signed=False)  # sys.byteorder
        # Hash it
        # hashed = hash(value_bytes)
        hashed = zlib.crc32(value_bytes)
        # Ensure 32 bit output
        return hashed & 0xffffffff

def calc_next_hop (ran, i):
    val = ran + 2 ** 16 * i
    hashed = my_hash(val)
    modulo = hashed % 35
    channel = 8 * modulo
    return channel+8

n_frames = 500 # como máximo, el dispositivo solo creará 500 frames.
ran = np.random.randint(2**9) # num random para el dispositivo
offsets = [2 ** 16 * i for i in range(500)]
for frame_i in range(n_frames):
    if calc_next_hop(ran, frame_i) == 0: #puede devolver uno de estos: [8*0, 8*1, 8*2, ... ,8*34] 
        print(f'ran = {ran}, i = {frame_i}')
