import numpy as np

class Modulation:
    # LoRa Collision matrix (used in ns-3 implementation for LoRa interferences)
    #                        SF7  SF8     SF9     SF10    SF11    SF12 
    sinr = np.array ([      [6,  -16,    -18,    -19,    -19,    -20],  # SF7
                            [-24,  6,    -20,    -22,    -22,    -22],  # SF8
                            [-27, -27,     6,    -23,    -25,    -25],  # SF9
                            [-30, -30,   -30,      6,    -26,    -28],  # SF10
                            [-33, -33,   -33,    -33,      6,    -29],  # SF11
                            [-36, -36,   -36,    -36,    -36,      6]]) # SF12

    rx_sensitivity = np.array([-124, -127, -130, -133, -135, -137]) #(in dBm)
    
    def __init__(self, data_rate):
        """Initializes a Modulation instance

        Args:
            data_rate (int): data rate.
        """
        self.data_rate = data_rate
        if self.data_rate == 8:
            self.mod_name = "FHSS"
            self.num_subch = 280
            self.bitrate = 162
            self.num_hdr_replicas = 3
            self.numerator_codrate = 1
            self.hop_duration = 50
            self.num_usable_freqs = 35
        
        elif self.data_rate == 9:
            self.mod_name = "FHSS"
            self.num_subch = 280
            self.bitrate = 325
            self.num_hdr_replicas = 2
            self.numerator_codrate = 2
            self.hop_duration = 50
            self.num_usable_freqs = 35

        elif self.data_rate == 10:
            self.mod_name = "FHSS"
            self.num_subch = 688
            self.bitrate = 162
            self.num_hdr_replicas = 3
            self.numerator_codrate = 1
            self.hop_duration = 50
            self.num_usable_freqs = 86

        elif self.data_rate == 11:
            self.mod_name = "FHSS"
            self.num_subch = 688
            self.bitrate = 325
            self.num_hdr_replicas = 2
            self.numerator_codrate = 2
            self.hop_duration = 50
            self.num_usable_freqs = 86

        else:
            self.mod_name = "CSS"
            self.num_subch = 1
            self.bitrate = 0
            self.num_hdr_replicas = 1
            self.numerator_codrate = 0
            self.hop_duration = None
            self.num_usable_freqs = 1
    
    def get_data_rate (self):
        """Gets the data rate

        Returns:
            int: data rate
        """
        return self.data_rate

    def get_mod_name (self):
        """Gets the modulation name

        Returns:
            str: modulation name ("CSS" or "FHSS" at the moment)
        """
        return self.mod_name

    def get_num_subch(self):
        """Gets the number of subchannels

        Returns:
            int: number of subchannels
        """
        return self.num_subch

    def get_bitrate(self):
        """Gets the bitrate

        Returns:
            int: bit rate
        """
        return self.bitrate

    def get_num_hdr_replicas(self):
        """Gets the number of header replicas

        Returns:
            int: number of header replicas (>1 for FHSS modulation devices)
        """
        return self.num_hdr_replicas

    def get_numerator_codrate(self):
        """Gets the code rate numerator

        Returns:
            int: code rate numerator
        """
        return self.numerator_codrate

    def get_hop_duration(self):
        """Gets the hop duration

        Returns:
            int: hop duration (ms)
        """
        return self.hop_duration

    def get_num_usable_freqs(self):
        """Gets the number of usable frequencies

        Returns:
            int: number of usable frequencies
        """
        return self.num_usable_freqs

    def get_data(self):
        """Gets modulation data in a dictionary

        Returns:
            dict: dictionary with modulation information
        """
        mod_data = dict()
        mod_data["data_rate"] = self.data_rate
        mod_data["mod_name"] = self.mod_name
        mod_data["num_subch"] = self.num_subch
        mod_data["bitrate"] = self.bitrate
        mod_data["num_hdr_replicas"] = self.num_hdr_replicas
        mod_data["numerator_codrate"] = self.numerator_codrate
        mod_data["hop_duration"]=self.hop_duration
        mod_data["num_usable_freqs"]=self.num_usable_freqs
        return mod_data