import numpy as np
import zlib

class SequenceGenerator:

    def __init__(self, n_channels, n_bits, n_usable_freqs):
        """Initializes a SequenceGenerator instance.

        In FHSS, devices communicate according to various channel hopping schemes, with each subsequent transmission
        utilizing the next channel defined in a hopping sequence.

        Args:
            n_channels (int): Number of available subchannels for frequency hopping
            n_bits (int): number of bits in LoRa-E packet with frequency hopping information
            n_usable_freqs (int): number of usable frequencies considering minimum frequency shift.
        """ 
        self.n_channels = n_channels
        self.n_bits = n_bits
        self.n_usable_freqs = n_usable_freqs
        self.min_ch_dist_eu = 8

        #Produces a random number from which the sequence will be generated
        self.seq_seed = np.random.randint(0, 2**self.n_bits - 1)


    def generate_next_hop_channel(self, i):
        """ Generates the next channel to transmit on.
        
        The pattern is the output of a 32 bit hashing function then modulo the number of available channels

        Args:
            i (int): frame number

        Returns:
            (int): channel
        """

        if i == 0:
            self.next_seq = np.random.randint(0, self.n_channels)

        else:
            val = self.seq_seed + 2 ** 16 * i
            hashed = self.__my_hash(val)
            modulo = hashed % (self.n_usable_freqs-1)
            channel_hop = (self.min_ch_dist_eu * modulo) + 8
            assert abs(self.next_seq - ((self.next_seq + channel_hop) % self.n_channels)) >= 8, f'Consecutive TXs do not meet 8 channels distance requirement. frame={i}'
            self.next_seq = (self.next_seq + channel_hop) % self.n_channels
        
        return self.next_seq



    def __my_hash(self, value):
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