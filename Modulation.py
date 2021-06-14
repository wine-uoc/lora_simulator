class Modulation:

    def __init__(self, data_rate):
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
        return self.data_rate

    def get_mod_name (self):
        return self.mod_name

    def get_num_subch(self):
        return self.num_subch

    def get_bitrate(self):
        return self.bitrate

    def get_num_hdr_replicas(self):
        return self.num_hdr_replicas

    def get_numerator_codrate(self):
        return self.numerator_codrate

    def get_hop_duration(self):
        return self.hop_duration

    def get_num_usable_freqs(self):
        return self.num_usable_freqs

    def get_data(self):
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