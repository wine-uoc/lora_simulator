import os

import numpy as np

import DeviceHelper


# Received vs Generated frames


def get_t_off(_dr, _pl):
    if _dr < 8:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora(_pl, _dr)
        reps = 1
    elif _dr == 8 or _dr == 10:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 162)
        reps = 3
    elif _dr == 9 or _dr == 11:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 366)
        reps = 2
    else:
        print('Unknown')
        return 0.
    toa = reps * t_preamble + t_payload
    return DeviceHelper.DeviceHelper.get_off_period(toa, 0.01), toa


# Sim parameters
runs = 2
dvs = [10, 100, 1000, 3000, 5000]
pls = [10]
drs = [8]

# de 1 pkt/h a 50 (el dc limita abans darribar a 50)
lmbd = np.arange(1, 50, 2)
# Conversion to transmission interval in simulation units (ms)
tx_intervals = list(np.round(1./lmbd * 3600000).astype(int))
# [3600000, 1200000, 720000, 514286, 400000, 327273, 276923, 240000, 211765, 189474, 171429, 156522, 144000, 133333,
# 124138, 116129, 109091, 102857, 97297, 92308, 87805, 83721, 80000, 76596, 73469]


for dr in drs:
    for pl in pls:
        for devices in dvs:
            for interval in tx_intervals:
                toff, toa = get_t_off(dr, pl)
                skip = interval < toff  # (toa + toff)
                if skip:
                    print('Limit because duty cycle regulation ...')
                    interval = toff
                for i in range(runs):
                    # check if already simulated
                    f_name = './results/dr' + str(dr) + '/pl' + str(pl) + '/' + str(devices) + '_' + str(interval) + '_' + str(i) + '.npy'
                    if os.path.isfile(f_name):
                        print('Skipping ...')
                        print(f_name)
                    else:
                        os.system('python3 Test.py' +
                                  ' -r ' + str(i) +
                                  ' -d ' + str(devices) +
                                  ' -t ' + str(interval) +
                                  ' -pl ' + str(pl) +
                                  ' -dr ' + str(dr)
                                  )