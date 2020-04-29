import matplotlib.pyplot as plt
import numpy as np


def plot_cross_corr(x_, y_):
    """Cross-correlation."""
    plt.xcorr(x_, y_, normed=False)
    plt.show()


def plot_auto_corr(seq):
    """Linear auto-correlation should be approximately an impulse if random."""
    N = len(seq)
    a_corr = np.correlate(seq, seq, mode='full')
    plt.figure()
    plt.plot(np.arange(-N + 1, N), a_corr, '.-')
    plt.margins(0.1, 0.1)
    plt.grid(True)
    plt.show()


class CodesHelper:
    """
    _seq methods return a matrix of size (n_devices, n_hops) with sequences generated accordingly to method selected
    """

    @staticmethod
    def lora_e_random_seq(n_channels, min_ch_dist, n_devices, duration):
        """
        Random sequences with minimum hop distance.
        :param min_ch_dist: minimum hop distance in channels
        :param n_channels: length of the set
        :param n_devices: number of devices in simulation
        :param duration: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, n_hops) with uniform random integers within range [0, n_channels)
        """
        assert n_channels > min_ch_dist
        # Pre alloc
        hop_seq = np.empty((n_devices, duration), dtype=int)

        for device in range(n_devices):
            hop_seq[device] = CodesHelper.sample_with_minimum_distance(n_channels, min_ch_dist, duration)

        return hop_seq

    @staticmethod
    def random_seq(n_channels, n_devices, duration):
        """
        Random sequences.
        :param n_channels: length of the set
        :param n_devices: number of devices in simulation
        :param duration: maximum number of freq. choices that a device can perform during simulation
        :return: matrix of size (n_devices, n_hops) with uniform random integers within range [0, n_channels)
        """
        return np.random.randint(0, n_channels, (n_devices, duration))

    @staticmethod
    def lfsr_seq(cycle_length, n_channels, n_devices, duration):
        """
        Randomly select next channel until cycle_length channels selected, then repeat sequence
        :param cycle_length: sequence period
        """
        # Generate one period of length (2**n_bits) - 1 for each node
        one_cycle = CodesHelper.random_seq(n_channels, n_devices, cycle_length)

        # Fit sequence to simulation length
        return CodesHelper.fit_seq_sim(one_cycle, duration)

    @staticmethod
    def circ_seq(cycle_length, n_channels, n_devices, duration):
        # Pre alloc
        one_cycle = np.empty((n_devices, cycle_length), dtype=int)

        # Generate matrix with circularly shifted by 1 sequences for each device
        next_seq = list(range(n_channels))
        one_cycle[0, :] = next_seq
        for i in range(1, n_devices):
            next_seq = CodesHelper.shift_left(next_seq, 1)
            one_cycle[i, :] = next_seq

        return CodesHelper.fit_seq_sim(one_cycle, duration)

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
        seq[0] = CodesHelper.random_seq(domain, 1, 1)[0][0]

        for i in range(1, samples):
            last_freq = seq[i-1]
            next_freq = CodesHelper.random_seq(domain, 1, 1)[0][0]

            while abs(last_freq - next_freq) < step:
                next_freq = CodesHelper.random_seq(domain, 1, 1)[0][0]

            seq[i] = next_freq

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

