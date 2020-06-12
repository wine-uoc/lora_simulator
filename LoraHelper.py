import math


class LoraHelper:

    # Returns a tuple with the following parameters: device_modulation, simulation_channels, device_tx_rate,
    # number_repetitions_header, numerator_coding_rate, hop_duration
    @staticmethod
    def get_configuration(dr_mode=None):
        assert (dr_mode is not None)

        if dr_mode == 8:  # CR=1/3, BW=137kHz, R=162bps
            return 'FHSS', 280, 162, 3, 1, 50
        elif dr_mode == 9:  # CR=2/3, BW=137kHz, R=366bps
            return 'FHSS', 280, 325, 2, 2, 50
        elif dr_mode == 10:  # CR=1/3, BW=336kHz, R=162bps
            return 'FHSS', 688, 162, 3, 1, 50
        elif dr_mode == 11:  # CR=2/3, BW=336kHz, R=366bps
            return 'FHSS', 688, 325, 2, 2, 50
        else:  # Assume regular LoRa
            # TODO: Why is hop_duration 50 ms for regular LoRa? Should it be N/A?
            # hop_duration is not used in LoRa but must be lower than simulation time
            return 'notFHSS', 1, 0, 1, 0, 50

    @staticmethod
    def get_time_on_air(modulation, dr_bps, pl_bytes, dr):
        """

        :param modulation:
        :param dr_bps:
        :param pl_bytes:
        :param dr:
        :return: total toa, preamble+header duration, pl duration
        """

        if modulation == 'FHSS':
            # LoRa-E
            t_h_ms, t_pl_ms = LoraHelper.toa_lora_e(pl_bytes, dr_bps)
            # get header repetitions to add to the total time
            if dr == 8 or dr == 10:
                reps = 3
            elif dr == 9 or dr == 11:
                reps = 2
            else:
                reps = 1
        else:
            # LoRa
            t_h_ms, t_pl_ms = LoraHelper.toa_lora(pl_bytes, dr)
            reps = 1
        return reps * round(t_h_ms + t_pl_ms), round(t_h_ms), round(t_pl_ms)

    @staticmethod
    def toa_lora_e(pl_bytes, dr_bps, dr=None):
        """
        Given DR mode return time on air (ms) for ONE header and payload
        :param pl_bytes:
        :param dr_bps: temporary
        :param dr:
        :return:
        """
        # # OLD
        # t_payload = 1000 * (pl_bytes * 8 + 16) / dr_bps  # [ms] +16 bc payload CRC is 2B
        # t_preamble = 1000 * 114 / dr_bps  # [ms] 114 = sync-word + (preamble + header) * CR2/1 + 2b

        # NEW
        if dr_bps == 162:
            t_payload = math.ceil((pl_bytes + 2) / 2) * 102
        elif dr_bps == 325:
            t_payload = math.ceil((pl_bytes + 2) / 4) * 102
        else:
            raise Exception('Unknown bitrate.')
        t_preamble = 233    # ms
        return t_preamble, t_payload

    @staticmethod
    def toa_lora(pl_bytes, dr=None):
        """
        Given DR mode return time on air for header and payload
        :param pl_bytes: pay_load_bytes
        :param dr: DR LoRa mode
        :return:
        """
        # LORA mode to SF
        if dr == 0:
            sf = 12
        elif dr == 1:
            sf = 11
        elif dr == 2:
            sf = 10
        elif dr == 3:
            sf = 9
        elif dr == 4:
            sf = 8
        elif dr == 5:
            sf = 7
        else:
            raise Exception('Unknown DR mode.')
        bw = 125  # 125 (default) or 250 [kHz]

        # Default LoRa configuration
        n_preamble = 8  # 8 (default) or 10 preamble length [sym]
        header = True
        cr = 1  # CR in the formula 1 (default) to 4
        crc = True  # CRC for up-link
        IH = not header  # Implicit header
        if sf == 6:  # can only have implicit header with SF6
            IH = True
        DE = bw == 125 and sf >= 11  # Low Data Rate Optimization

        r_sym = (bw * 1000) / (2 ** sf)
        t_sym = 1. / r_sym * 1000  # [ms]
        t_preamble = (n_preamble + 4.25) * t_sym  # [ms]

        beta = math.ceil(
            (8 * pl_bytes - 4 * sf + 28 + 16 * crc - 20 * IH) / (4 * (sf - 2 * DE))
        )
        n_payload = 8 + max(beta * (cr + 4), 0)
        t_payload = n_payload * t_sym

        return t_preamble, t_payload

    @staticmethod
    def get_duty_cycle(t_air):
        """Return tx interval (one message every ...) for duty cycle 1%"""
        return round((t_air / 600) * 60) * 1000

    @staticmethod
    def get_off_period(t_air, dc):
        """Return minimum off-period"""
        return round(t_air * (1. / dc - 1))
