class LoraHelper:

    # Returns a tuple with the following parameters:
    # device_modulation, simulation_channels, device_tx_rate, number_repetitions_header, numerator_conding_rate, hop_duration
    @staticmethod
    def get_configuration(dr_mode=None):
        assert (dr_mode != None)

        if (dr_mode == 8):  # CR=1/3, BW=137kHz, R=162bps
            return ('FHSS', 280, 162, 3, 1, 50)
        elif (dr_mode == 9):  # CR=2/3, BW=137kHz, R=366bps
            return ('FHSS', 280, 366, 2, 2, 50)
        elif (dr_mode == 10): # CR=1/3, BW=336kHz, R=162bps
            return (None, None, None, None, None, None)
        elif (dr_mode == 11): # CR=2/3, BW=336kHz, R=366bps
            return ('FHSS', 688, 366, 2, 2, 50)
        else: # Assume regular LoRa
            # TODO: Why is hop_duration 50 ms for regular LoRa? Should it be N/A?
            return ('notFHSS', 1, 0, 1, 0, 50)