import zlib

import numpy as np


class SequenceHelper:
    """
    _seq methods return a matrix of size (n_devices, n_hops) with sequences generated accordingly to method selected
    """

    @staticmethod
    def lora_e_hash(n_channels, min_ch_dist, n_devices, duration, n_bits):
        """
        LoRa-E random sequences using 32 bit hash function.
        :param n_bits:
        :param n_channels: length of the set
        :param n_devices: number of devices in simulation
        :param duration: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, duration)
        """
        # Pre alloc
        hop_seq = np.empty((n_devices, duration), dtype=int)

        # n_bits-bit random number for each device
        ran = SequenceHelper.random_seq(domain=2**n_bits - 1, n_devs=n_devices, dur=1)

        # number of physical carriers usable for channel hopping
        n_ch_available = int(n_channels / min_ch_dist)

        # Get sequence
        for device in range(n_devices):
            for frame in range(duration):
                hop_seq[device, frame] = SequenceHelper.calc_next_hop_hash(ran[device][0], frame, n_ch_available, min_ch_dist)

        return hop_seq

    @staticmethod
    def lora_e_random_seq_limited(cycle_length, n_channels, min_ch_dist, n_devices, duration):
        """
        Random sequences with minimum hop distance limited to sets of cycle_length.
        :param min_ch_dist: minimum hop distance in channels
        :param n_channels: length of the set
        :param n_devices: number of devices in simulation
        :param duration: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, duration) with uniform random integers within range [0, n_channels)
        """
        assert n_channels > min_ch_dist

        # Pre alloc
        one_cycle = np.empty((n_devices, cycle_length), dtype=int)

        # Generate one period of length cycle_length for each node
        for device in range(n_devices):
            one_cycle[device] = SequenceHelper.sample_with_minimum_distance(n_channels, min_ch_dist, cycle_length)

        # Fit sequence to simulation length
        return SequenceHelper.fit_seq_sim(one_cycle, duration)

    @staticmethod
    def lora_e_random_seq(n_channels, min_ch_dist, n_devices, duration):
        """
        Random sequences with minimum hop distance.
        :param min_ch_dist: minimum hop distance in channels
        :param n_channels: length of the set
        :param n_devices: number of devices in simulation
        :param duration: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, duration) with uniform random integers within range [0, n_channels)
        """
        assert n_channels > min_ch_dist
        # Pre alloc
        hop_seq = np.empty((n_devices, duration), dtype=int)

        for device in range(n_devices):
            hop_seq[device] = SequenceHelper.sample_with_minimum_distance(n_channels, min_ch_dist, duration)

        return hop_seq

    @staticmethod
    def random_seq(domain, n_devs, dur):
        """
        Random sequences  within range [0, set).
        :param domain: length of the domain
        :param n_devs: number of devices in simulation
        :param dur: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, duration) with uniform random integers
        """
        return np.random.randint(0, domain, (n_devs, dur))

    @staticmethod
    def lfsr_seq(cycle_length, n_channels, n_devices, duration):
        """
        Randomly select next channel until cycle_length channels selected, then repeat sequence
        :param cycle_length: sequence period
        """
        # Generate one period of length (2**n_bits) - 1 for each node
        one_cycle = SequenceHelper.random_seq(n_channels, n_devices, cycle_length)

        # Fit sequence to simulation length
        return SequenceHelper.fit_seq_sim(one_cycle, duration)

    @staticmethod
    def circ_seq(cycle_length, n_channels, n_devices, duration):
        # Pre alloc
        one_cycle = np.empty((n_devices, cycle_length), dtype=int)

        # Generate matrix with circularly shifted by 1 sequences for each device
        next_seq = list(range(n_channels))
        one_cycle[0, :] = next_seq
        for i in range(1, n_devices):
            next_seq = SequenceHelper.shift_left(next_seq, 1)
            one_cycle[i, :] = next_seq

        return SequenceHelper.fit_seq_sim(one_cycle, duration)

    @staticmethod
    def fit_seq_sim(seq, sim_duration):
        """
        Fit a sequence of duration x to simulation duration y
        :param seq: original seq
        :param sim_duration: length of simulation in hop number
        :return: a full sequence with original seq repeated
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

    @staticmethod
    def shift_left(arr, n=0):
        """Return shifted (circular) array n positions."""
        return arr[n::] + arr[:n:]

    @staticmethod
    def sample_with_minimum_distance(domain, step, samples):
        assert step < domain

        seq = np.empty(samples, dtype=int)
        seq[0] = SequenceHelper.random_seq(domain, 1, 1)[0][0]

        for i in range(1, samples):
            last_freq = seq[i - 1]
            next_freq = SequenceHelper.random_seq(domain, 1, 1)[0][0]

            while abs(last_freq - next_freq) < step:
                next_freq = SequenceHelper.random_seq(domain, 1, 1)[0][0]

            seq[i] = next_freq

        # Fix last frequency
        first_freq = seq[0]
        pen_freq = seq[-2]
        last_freq = seq[-1]
        while abs(last_freq - first_freq) < step or abs(last_freq - pen_freq) < step:
            last_freq = SequenceHelper.random_seq(domain, 1, 1)[0][0]

        return seq

    @staticmethod
    def gen_phy_m_seq(n_devices, n_bits):
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

    @staticmethod
    def calc_next_hop_hash(ran_, i_, n_ch, min_ch_dist):
        """
        The pattern is the output of a 32 bit hashing function then modulo the number of available channels
        """
        val = ran_ + 2 ** 16 * i_
        hashed = SequenceHelper.my_hash(val)
        modulo = hashed % n_ch
        channel = min_ch_dist * modulo
        return channel

    @staticmethod
    def my_hash(value):
        # Define our int to bytes conversion procedure
        value_bytes = int(value).to_bytes(8, 'big', signed=False)  # sys.byteorder
        # Hash it
        # hashed = hash(value_bytes)
        hashed = zlib.crc32(value_bytes)
        # Ensure 32 bit output
        return hashed & 0xffffffff


# import matplotlib.pyplot as plt
#
# def plot_cross_corr(x_, y_):
#     """Cross-correlation."""
#     plt.xcorr(x_, y_, normed=False)
#     plt.show()
#
# def plot_auto_corr(seq):
#     """Linear auto-correlation should be approximately an impulse if random."""
#     N = len(seq)
#     a_corr = np.correlate(seq, seq, mode='full')
#     plt.figure()
#     plt.plot(np.arange(-N + 1, N), a_corr, '.-')
#     plt.margins(0.1, 0.1)
#     plt.grid(True)
#     plt.show()