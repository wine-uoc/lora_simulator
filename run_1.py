import os

import DeviceHelper


# Received vs Generated frames


def get_t_off(_dr, _pl):
    if _dr < 8:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora(_pl, _dr)
        reps = 1
    elif _dr == 8:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 162)
        reps = 3
    elif _dr == 11:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 366)
        reps = 2
    else:
        print('Unknown')
        return 0.
    return DeviceHelper.DeviceHelper.get_off_period(reps * t_preamble + t_payload, 0.01)


# Sim parameters
runs = 2
dvs = [100, 300, 900]
pls = [10, 50]
drs = [0, 5, 8, 11]     # 0, 5 is LoRa; 8, 11 is LoRa-E
tx_intervals = [360000, 180000, 90000, 32727, 17143, 11613, 8780, 7059, 5902, 5070, 4444, 3956, 2500, 1000]


for dr in drs:
    for pl in pls:
        for devices in dvs:
            for interval in tx_intervals:
                t_off = get_t_off(dr, pl)
                if interval < t_off:
                    print('Skipping because duty cycle limitation ...')
                else:
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