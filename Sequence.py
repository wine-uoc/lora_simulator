import numpy as np
import logging
import zlib

logger = logging.getLogger(__name__)

class Sequence:
    def __init__(self, interval, n_channels, 
                data_rate, n_bits, type, time_sim, 
                hop_duration, n_usable_freqs, num_devices):
        """Initializes a Sequence instance.

        In FHSS, devices communicate according to various channel hopping schemes, with each subsequent transmission
        utilizing the next channel defined in a hopping sequence.

        Args:
            interval (int): Transmit interval for each device (ms)
            n_channels (int): Number of available subchannels for frequency hopping
            data_rate (int): LoRa-E data rate
            n_bits (int): number of bits in LORA-E packet with frequency hopping information
            type (str): the method to generate the hopping sequence
            time_sim (int): Duration of the simulation in milliseconds
            hop_duration (int): The duration in ms of a frequency hop
            n_usable_freqs (int): number of usable frequencies considering minimum frequency shift.
            num_devices (int): number of devices in simulation
        """ 
        self.interval = interval
        self.n_channels = n_channels
        self.data_rate = data_rate
        self.n_bits = n_bits
        self.type = type
        self.time_sim = time_sim
        self.hop_duration = hop_duration
        self.n_usable_freqs = n_usable_freqs
        self.n_devices = num_devices

        self.cycle_length = 0
        self.min_ch_dist_eu = 8

        if self.interval == 'max':
            self.n_hops = int((self.time_sim / 4000) * self.hop_duration)
        else:
            self.n_hops = int((self.time_sim / self.interval) * self.hop_duration)

        self.__generate_hopping_sequences()

    def get_hopping_sequences(self):
        """Gets hopping sequence matrix

        Returns:
            matrix: matrix of shape (n_devices, n_hops) with frequencies
        """
        return self.hop_seqs

    def __generate_hopping_sequences(self):
        """Get a generated hopping sequence

        Returns:
            matrix: frequency hop sequence for each device
        """        
        if self.type == "random":
            # Infinite random Sequence
            self.cycle_length = -1
            self.hop_seqs = self.__generate_random_seq(self.n_channels,self.n_devices, self.n_hops)
        elif self.type == "LFSR":
            # m-sequences (Maximal Length Linear Feedback Shift Register sequences)
            self.cycle_length = (2 ** self.n_bits) - 1
            self.hop_seqs = self.__generate_lfsr_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)
        elif self.type == "circular":
             # Easy orthogonal sequence implementation for time synchronized devices
            self.cycle_length = self.n_channels
            self.hop_seqs = self.__generate_circ_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)
        elif self.type == "lora-e-eu-inf":
            # Infinite random Sequence with EU minimum hop distance
            self.cycle_length = -1
            self.hop_seqs = self.__generate_lora_e_random_seq(self.n_channels, self.min_ch_dist_eu, self.n_devices, self.n_hops)
        elif self.type == 'lora-e-eu-hash':
            # Cyclical random Sequence with EU minimum hop distance
            self.cycle_length = -1
            self.hop_seqs = self.__generate_lora_e_hash(self.n_channels, self.min_ch_dist_eu, self.n_devices, self.n_hops, self.n_bits)
        elif self.type == "lora-e-eu-cycle":
            # Cyclical random Sequence with EU minimum hop distance
            self.cycle_length = self.n_usable_freqs
            self.hop_seqs = self.__generate_lora_e_random_seq_limited(self.cycle_length, self.n_channels, self.min_ch_dist_eu, self.n_devices, self.n_hops)
        else:
            logger.error('Unknown type of code sequence selected.')
        
        return self.hop_seqs

    def __generate_random_seq(self, n_channels, n_devices, duration):
        """Generate random sequences within range [0, n_channels]

        Args:
            n_channels (int): num of channels
            n_devices (int): num of devices
            duration (int): num of hops 

        Returns:
            matrix: matrix of size (n_devices, duration) with uniform random integers
        """        
        return np.random.randint(0, n_channels, (n_devices, duration))

    def __generate_lfsr_seq(self, cycle_length, n_channels, n_devices, duration):
        """Randomly select next channel until cycle_length channels selected, then repeat sequence

        Args:
            cycle_length (int): sequence period
            n_channels (int): num of channels
            n_devices (int): num of devices
            duration (int): num of hops

        Returns:
            matrix: matrix of size (n_devices, duration) with frequency hop sequence
        """   

        # Generate one period of length (2**n_bits) - 1 for each node     
        one_cycle = self.__generate_random_seq(n_channels, n_devices, cycle_length)
        # Fit sequence to simulation length
        return self.__fit_seq_sim(one_cycle, duration)

    def __generate_circ_seq(self, cycle_length, n_channels, n_devices, duration):
        """Generate matrix with circularly shifted by 1 sequences for each device

        Args:
            cycle_length (int): sequence period
            n_channels (int): num of channels
            n_devices (int): num of devices
            duration (int): num of hops

        Returns:
            matrix: matrix of shape (n_devices, duration) with frequency hop sequence
        """
        
        # Pre alloc
        one_cycle = np.empty((n_devices, cycle_length), dtype=int)

        # Generate matrix with circularly shifted by 1 sequences for each device
        next_seq = list(range(n_channels))
        one_cycle[0, :] = next_seq
        for i in range(1, n_devices):
            next_seq = self.__shift_left(next_seq, 1)
            one_cycle[i, :] = next_seq   

        return self.__fit_seq_sim(one_cycle, duration)
        
    def __generate_lora_e_random_seq(self, n_channels, min_ch_dist, n_devices, duration):
        """Random sequences with minimum hop distance.

        Args:
            n_channels (int): length of the set
            min_ch_dist (int): minimum hop distance in channels
            n_devices (int): number of devices in simulation
            duration (int): maximum number of freq. choices that a device can perform during simulation

        Returns:
            matrix: matrix of size (n_devices, duration) with uniform random integers within range [0, n_channels)
        """

        assert n_channels > min_ch_dist

        # Pre alloc
        hop_seq = np.empty((n_devices, duration), dtype=int)

        for device in range(n_devices):
            hop_seq[device] = self.__sample_with_minimum_distance(n_channels, min_ch_dist, duration)

        return hop_seq
    
    def __generate_lora_e_hash(self, n_channels, min_ch_dist, n_devices, duration, n_bits):
        """LoRa-E random sequences using 32 bit hash function.

        Args:
            n_channels (int): length of the set
            min_ch_dist (int): minimum hop distance in channels
            n_devices (int): number of devices in simulation
            duration (int): maximum number of freq. choices that a device can perform during simulation
            n_bits (int): num of bits of random number

        Returns:
            matrix: matrix of size (n_devices, duration)
        """

          # Pre alloc
        hop_seq = np.empty((n_devices, duration), dtype=int)

        # n_bits-bit random number for each device
        ran = self.__generate_random_seq(2**n_bits - 1, n_devices=n_devices, duration=1)

        # number of physical carriers usable for channel hopping
        n_ch_available = int(n_channels / min_ch_dist)

        # Get sequence
        for device in range(n_devices):
            for frame in range(duration):
                hop_seq[device, frame] = self.__calc_next_hop_hash(ran[device][0], frame, n_ch_available, min_ch_dist)

        return hop_seq
        
    def __generate_lora_e_random_seq_limited(self, cycle_length, n_channels, min_ch_dist, n_devices, duration):
        """Random sequences with minimum hop distance limited to sets of cycle_length.

        Args:
            cycle_length (int): sequence period
            n_channels (int): length of the set
            min_ch_dist (int): minimum hop distance in channels
            n_devices (int): number of devices in simulation
            duration (int):  maximum number of freq. choices that a device can perform during simulation

        Returns:
            matrix: matrix of size (n_devices, duration) with uniform random integers within range [0, n_channels)
        """
        assert n_channels > min_ch_dist

        # Pre alloc
        one_cycle = np.empty((n_devices, cycle_length), dtype=int)

        # Generate one period of length cycle_length for each node
        for device in range(n_devices):
            one_cycle[device] = self.__sample_with_minimum_distance(n_channels, min_ch_dist, cycle_length)

        # Fit sequence to simulation length
        return self.__fit_seq_sim(one_cycle, duration)

    def __fit_seq_sim(self, seq, sim_duration):
        """Fits a sequence of duration seq.shape[0] to sim_duration 

        Args:
            seq ([int] or matrix): original sequence
            sim_duration (int): length of simulation in hop number

        Returns:
            matrix: a full sequence with original sequence repeated
        """

        n_devices, seq_duration = seq.shape
        if seq_duration >= sim_duration:
            return seq[:, :sim_duration]
        else:
            # Pre alloc
            full_seq = np.empty((n_devices, sim_duration), dtype=int)

            # Get number of repetitions
            n_cycles = sim_duration // seq_duration
            last_part_length = sim_duration % seq_duration

            # Repeat until end of simulation
            for cycle in range(n_cycles):
                full_seq[:, seq_duration * cycle:seq_duration * (cycle + 1)] = seq

            if last_part_length != 0:
                full_seq[:, -last_part_length:] = seq[:, :last_part_length]

            return full_seq

    def __shift_left(self, arr, n=0):
        """Return shifted (circular) array n positions.

        Args:
            arr [int]: list of channels
            n (int, optional): number of positions to shift. Defaults to 0.

        Returns:
            [int]: arr sequence shifted left n positions
        """
        return arr[n::] + arr[:n:]

    def __sample_with_minimum_distance (self, domain, step, samples):
        """Creates a sequence seq of samples length containing frequencies. Each seq[i] keeps a minimum distance
        step with seq[i-1] and seq[i+1] frequencies.

        Args:
            domain (int): num of channels
            step (int): minimum hop distance
            samples (int): num of usable frequencies

        Returns:
            [int]: sequence of suitable frequencies for frequency hopping transmission
        """
        assert step < domain

        seq = np.empty(samples, dtype=int)
        seq[0] = self.__generate_random_seq(domain, 1, 1)[0][0]

        for i in range(1, samples):
            last_freq = seq[i - 1]
            next_freq = self.__generate_random_seq(domain, 1, 1)[0][0]

            while abs(last_freq - next_freq) < step:
                next_freq = self.__generate_random_seq(domain, 1, 1)[0][0]

            seq[i] = next_freq

        # Fix last frequency
        first_freq = seq[0]
        pen_freq = seq[-2]
        last_freq = seq[-1]
        while abs(last_freq - first_freq) < step or abs(last_freq - pen_freq) < step:
            last_freq = self.__generate_random_seq(domain, 1, 1)[0][0]

        return seq

    def __calc_next_hop_hash(self, ran_, i_, n_ch, min_ch_dist):
        """The pattern is the output of a 32 bit hashing function then modulo the number of available channels

        Args:
            ran_ (int): random number
            i_ (int): frame number
            n_ch (int): number of usable frequencies for frequency hopping
            min_ch_dist (int): minimum hop distance in channels

        Returns:
            (int): frequency 
        """
        val = ran_ + 2 ** 16 * i_
        hashed = self.__my_hash(val)
        modulo = hashed % n_ch
        channel = min_ch_dist * modulo
        return channel

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

    def __gen_phy_m_seq(self, n_devices, n_bits):
        # NOT USED ANYWHERE!
        """Example of how to generate m-sequences of bit codes at PHY level."""
        from scipy.signal import max_len_seq

        # Generate initial states of registers for each node
        states = np.random.randint(0, 1 + 1, (n_devices, n_bits))

        # Avoid the all-zero state
        while np.any(np.sum(states == 0, axis=1) == 9):
            states = np.random.randint(0, 1 + 1, (n_devices, n_bits))

        # Generate BIT sequence of length 2^n_bits - 1 for each node
        bit_seq = []
        for i in range(n_devices):
            bit_seq.append(max_len_seq(n_bits, state=states[i], length=None, taps=None))

        return bit_seq