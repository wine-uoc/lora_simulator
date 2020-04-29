import math

import matplotlib.pyplot as plt


class DeviceHelper:

    @staticmethod
    def get_time_on_air(modulation, dr_bps, pl_bytes):

        if modulation == 'FHSS':
            # LoRa-E
            t_pl_ms = 1000 * (pl_bytes * 8 + 16) / dr_bps   # +16 bc payload CRC is 2B
            t_h_ms = 1000 * 114 / dr_bps                    # LoRa-E: 114 = syncword + (preamble + header) * CR2/1 + 2b
        else:
            # LoRa
            t_h_ms, t_pl_ms = DeviceHelper.lora(pl_bytes)

        return int(t_h_ms), int(t_pl_ms)

    @staticmethod
    def lora(pay_load_bytes, dr=None):
        """
        Given DR mode return time on air for header and payload
        :param pay_load_bytes:
        :param dr: DR LoRa mode
        :return:
        """
        # LORA mode
        n_sf = 12
        n_bw = 125
        n_size = pay_load_bytes

        n_cr = 1    # CR in the fomula
        v_DE = 1    # Low Data Rate Optimization if sf 11, 12
        v_IH = 0    # Implicit header
        v_CRC = 1   # CRC for uplink
        n_preamble = 8  # default preamble length in bit

        r_sym = (n_bw * 1000.) / math.pow(2, n_sf)
        t_sym = 1000. / r_sym

        t_preamble = (n_preamble + 4.25) * t_sym
        a = 8. * n_size - 4. * n_sf + 28 + 16 * v_CRC - 20. * v_IH
        b = 4. * (n_sf - 2. * v_DE)
        n_payload = 8 + max(math.ceil(a / b) * (n_cr + 4), 0)
        t_payload = n_payload * t_sym

        return t_preamble, t_payload

    @staticmethod
    def plot_device_position(device_list=None, map_size=None):
        assert (device_list is not None)
        assert (map_size is not None)

        x_size, y_size = map_size
        device_positions = []
        for d in device_list:
            device_positions.append(d.get_position())

        x, y = zip(*device_positions)
        plt.scatter(x, y, color='b')

        plt.xlim((0, x_size))
        plt.ylim((0, y_size))
        plt.grid()
        plt.show()
