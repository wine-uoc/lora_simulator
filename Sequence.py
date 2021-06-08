import numpy as np

import SequenceHelper


class Sequence:

    def __init__(self, modulation, n_devices, n_bits, n_channels, n_hops, seq_type, dr):
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
        self.dr = dr

        self.cycle_length = 0       # The period of the sequence
        self.min_ch_dist_eu = 8

        # Pre alloc
        if modulation == 'FHSS':
            self.hopping_sequence = np.empty((self.n_devices, self.n_hops), dtype=int)

            if seq_type == 'random':
                # Infinite random Sequence
                self.cycle_length = -1  # infinite sequence
                self.hopping_sequence = SequenceHelper.SequenceHelper.random_seq(self.n_channels, self.n_devices, self.n_hops)

            elif seq_type == 'LFSR':
                # m-sequences (Maximal Length Linear Feedback Shift Register sequences)
                self.cycle_length = (2 ** n_bits) - 1   # -1 bc all-zero initial state of registers always returns 0
                self.hopping_sequence = SequenceHelper.SequenceHelper.lfsr_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)

            elif seq_type == 'circular':
                # Easy orthogonal sequence implementation for time synchronized devices
                self.cycle_length = self.n_channels
                self.hopping_sequence = SequenceHelper.SequenceHelper.circ_seq(self.cycle_length, self.n_channels, self.n_devices, self.n_hops)

            elif seq_type == 'lora-e-eu-inf':
                # Infinite random Sequence with EU minimum hop distance
                self.hopping_sequence = SequenceHelper.SequenceHelper.lora_e_random_seq(self.n_channels, self.min_ch_dist_eu, self.n_devices, self.n_hops)
                self.cycle_length = -1

            elif seq_type == 'lora-e-eu-hash':
                # Cyclical random Sequence with EU minimum hop distance
                self.hopping_sequence = SequenceHelper.SequenceHelper.lora_e_hash(self.n_channels, self.min_ch_dist_eu,  self.n_devices, self.n_hops, self.n_bits)
                self.cycle_length = -1

            elif seq_type == 'lora-e-eu-cycle':
                # Cyclical random Sequence with EU minimum hop distance
                if self.dr == 8 or self.dr == 9:
                    self.cycle_length = 35
                elif self.dr == 10 or self.dr == 11:
                    self.cycle_length = 86
                else:
                    raise Exception('N/A')
                self.hopping_sequence = SequenceHelper.SequenceHelper.lora_e_random_seq_limited(self.cycle_length, self.n_channels, self.min_ch_dist_eu, self.n_devices, self.n_hops)

            else:
                print('Unknown type of code sequence selected.')
        else:
            # modulation is plan LoRa, no hop sequence is needed
            self.hopping_sequence = np.zeros((self.n_devices, 1), dtype=int)

    def get_hopping_sequence(self, device_id):
        """Return LIST of frequency sequence assigned to the device id."""
        return self.hopping_sequence[device_id].tolist()




