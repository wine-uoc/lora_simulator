import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import max_len_seq


def plot_cross_corr(x_, y_):
    plt.xcorr(x_, y_, normed=False)
    plt.show()


def plot_auto_corr(seq):
    """Linear autocorrelation should be approximately an impulse if random."""
    N = len(seq)
    acorr = np.correlate(seq, seq, mode='full')
    plt.figure()
    plt.plot(np.arange(-N + 1, N), acorr, '.-')
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

        :param n_devices: number of devices
        :param n_bits: number of bits in LORA-E packet associated to frequency hopping
        :param n_channels: number of channels that a device can hop
        :param n_hops: maximum number of hops during simulation (if device starts transmitting at time=0)
        :param seq_type: method to generate sequence
        """
        self.n_devices = n_devices
        self.n_bits = n_bits
        self.n_channels = n_channels
        self.n_hops = int(n_hops)
        self.seq_type = seq_type

        self.cycle_length = (2 ** n_bits) - 1

        # pre alloc
        self.hopping_sequence = np.empty((self.n_devices, self.n_hops), dtype=int)

        # TODO:
        #  + implement exact LORA-E:
        #       o For each packet, randomly select a channel amongst the ones enabled
        #       o Frequency hopping on sub-channels inside the selected channel
        #  + implement other methods, such as
        #       o sequences selected to achieve a maximum gap between two consecutive frequencies (ISA 100 standard?)

        if seq_type == 'random':
            # Random Sequences [The Global Positioning System: Signals, measurements, and performance, Per K. Enge]:
            # (...) random codes provide a powerful design guide that allows us to estimate
            # performance of spread-spectrum signaling without designing any actual sequences (or flipping any coins).
            # Consideration of random codes allows the determination of the chipping rate and code lengths needed to
            # meet certain design criteria.
            self.hopping_sequence = np.random.randint(0, self.n_channels, (self.n_devices, self.n_hops))

        if seq_type == 'm-LFSR':
            # At PHY level, m-sequences (Maximal Length Linear Feedback Shift Register sequences) of bits
            # At MAC level: equivalent to randomly select next channel until (2**n_bits) - 1 channels selected,
            # then repeat sequence (-1 because all-zero initial state of Registers always will return 0)
            if self.cycle_length >= n_hops:
                self.hopping_sequence = np.random.randint(0, self.n_channels, (self.n_devices, self.n_hops))
            else:
                # Get number of repetitions
                n_cycles = int(np.floor(n_hops / self.cycle_length))
                last_part_length = int(n_hops % self.cycle_length)

                # Generate one period of length (2**n_bits) - 1 for each node
                one_cycle = np.random.randint(0, self.n_channels, (self.n_devices, self.cycle_length))

                # Repeat until end of simulation
                for cycle in range(n_cycles):
                    self.hopping_sequence[:, cycle * self.cycle_length:self.cycle_length * (cycle + 1)] = one_cycle
                self.hopping_sequence[:, -last_part_length:] = one_cycle[:, :last_part_length]

    def get_hopping_sequence(self, device_id):
        """Return LIST of frequency sequence assigned to the device id."""
        return self.hopping_sequence[device_id].tolist()    # use list() instead to preserve numpy data type int64

    def generate_phy_m_sequence(self):
        """Example of how bit codes are generated at PHY level."""
        # Generate initial states of registers for each node
        states = np.random.randint(0, 1 + 1, (self.n_devices, self.n_bits))

        # Avoid all-zero state
        # TODO more efficient implementation
        while np.any(np.sum(states == 0, axis=1) == 9):
            print('Avoiding the all-zero state ...')
            states = np.random.randint(0, 1 + 1, (self.n_devices, self.n_bits))

        # Generate BIT sequence of length 2^n_bits - 1 for each node
        bit_seq = []
        for i in range(self.n_devices):
            bit_seq.append(max_len_seq(self.n_bits, state=states[i], length=None, taps=None))

        return bit_seq


