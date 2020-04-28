import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import max_len_seq

import CodesHelper


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


class Codes:
    # n_devices = 10
    # n_bits = 9
    # n_channels = 5
    # n_hops = int(10000 / 50)
    # seq_type = 'random'
    # hopping_sequence = []

    def __init__(self, n_devices, n_bits, n_channels, n_hops, seq_type):
        """
        In FHSS, devices communicate according to various channel hopping schemes, with each subsequent transmission
        utilizing the next channel defined in a hopping sequence.

        :param n_devices: number of devices in simulation
        :param n_bits: number of bits in LORA-E packet with frequency hopping information
        :param n_channels: number of channels that the device is allowed to hop to
        :param n_hops: maximum number of hops during simulation
        :param seq_type: the method to generate the hopping sequence
        """
        self.n_devices = n_devices
        self.n_bits = n_bits
        self.n_channels = n_channels
        self.n_hops = int(n_hops)
        self.seq_type = seq_type

        # The period of the sequence
        self.cycle_length = 0

        # Pre alloc
        self.hopping_sequence = np.empty((self.n_devices, self.n_hops), dtype=int)

        # TODO:
        #  + implement exact LORA-E
        #  + implement other methods, such as
        #       - sequences selected to achieve a maximum gap between two consecutive frequencies (ISA 100 standard?)

        if seq_type == 'random':
            # Infinite random Sequence
            self.cycle_length = -1  # infinite sequence
            self.hopping_sequence = CodesHelper.CodesHelper.random_seq(self.n_channels, self.n_devices, self.n_hops)

        elif seq_type == 'LFSR':
            # m-sequences (Maximal Length Linear Feedback Shift Register sequences)
            self.cycle_length = (2 ** n_bits) - 1   # -1 bc all-zero initial state of registers always returns 0
            self.hopping_sequence = CodesHelper.CodesHelper.lfsr_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)

        elif seq_type == 'circular':
            # Easy orthogonal sequence implementation for time synchronized devices
            self.cycle_length = self.n_channels
            self.hopping_sequence = CodesHelper.CodesHelper.circ_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)

        elif seq_type == 'lora-e-eu-inf':
            # Infinite random Sequence with EU minimum hop distance
            self.cycle_length = -1
            self.hopping_sequence = CodesHelper.CodesHelper.lora_e_random_seq(self.n_channels, self.n_devices, self.n_hops)

        else:
            print('Unknown type of code sequence selected.')

    def get_hopping_sequence(self, device_id):
        """Return LIST of frequency sequence assigned to the device id."""
        return self.hopping_sequence[device_id].tolist()

    def gen_phy_m_seq(self):
        """Example of how to generate m-sequences of bit codes at PHY level."""
        # Generate initial states of registers for each node
        states = np.random.randint(0, 1 + 1, (self.n_devices, self.n_bits))

        # Avoid the all-zero state
        while np.any(np.sum(states == 0, axis=1) == 9):
            states = np.random.randint(0, 1 + 1, (self.n_devices, self.n_bits))

        # Generate BIT sequence of length 2^n_bits - 1 for each node
        bit_seq = []
        for i in range(self.n_devices):
            bit_seq.append(max_len_seq(self.n_bits, state=states[i], length=None, taps=None))

        return bit_seq


