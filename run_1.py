"""
Received vs Generated frames with variable transmission interval
"""
import os

import numpy as np

import DeviceHelper


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


python = "python3"
script = "Simulator.py"

result_file = './results/dr{}/pl{}/{}_{}_{}'
result_ext  = ".npy"

# Sim parameters
runs = 2
datarates = [0, 5, 8, 9]                # 0 to 5 is LoRa; 8 to 11 is LoRa-E
payloads  = [50]
devices   = [10, 100, 1000, 3000, 5000]
lmbd         = np.arange(1, 1000, 2)    # 1 pkt/h/node until 1000, will be limited by 0.01 DC for each data rate
tx_intervals = list(np.round(1. / lmbd * 3600000).astype(int))  # Conversion to tx interval in simulation units (ms)


# Execute for all datarates
for datarate in datarates:
    # Execute for all payloads
    for payload in payloads:
        # Execute for all devices
        for device in devices:
            # Check if number of devices to simulate makes sense for the data rate
            if device > 1000 and datarate < 8:
                print('Skipping. Mode DR= {} can not handle {} devices ...'.format(datarate, device))
            else:
                # Execute for all transmission intervals
                for interval in tx_intervals:
                    # Check if transmission interval is allowed by regulation
                    toff, toa = get_t_off(datarate, payload)
                    if interval <= toff:
                        print('Skipping. Transmission interval {} above limit {} by duty cycle.'.format(interval, toff))
                        interval = toff     # simulator already adds TOA
                    # Repeat for number of runs
                    for i in range(runs):
                        data_file = result_file.format(datarate, payload, device, interval, i) + result_ext
                        log_file = result_file.format(datarate, payload, device, interval, i)
                        # Check if already simulated
                        if os.path.isfile(data_file):
                            print('Skipping test {} as results already exist!'.format(data_file))
                        # Execute the simulation by calling the Simulator.py with the appropriate parameters
                        else:
                            print('Running test with parameters datarate={}, payload={}, devices={}, runs={}/{}.'.format(
                                datarate, payload, device, i + 1, runs))
                            command = "{} {} -r {} -d {} -t {} -pl {} -dr {} -l {}".format(python, script, i, device,
                                                                                           interval, payload, datarate,
                                                                                           log_file)
                            os.system(command)
