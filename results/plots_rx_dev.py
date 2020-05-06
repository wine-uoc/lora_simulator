import matplotlib.pyplot as plt
import numpy as np


# ------------------------------------------
# Received vs number of devices
# Maximum transmission rate
def get_rxed_gen_devices(_path, _devices_num, _runs):
    generated = []
    received = []
    devices = []
    for device in _devices_num:
        data_runs = np.zeros((len(runs), 2), dtype=float)
        for run in _runs:
            try:
                data_runs[run] = np.load(_path + str(device) + '_max_' + str(run) + '.npy')
                skip = False
            except:
                skip = True
        if not skip:
            devices.append(device)
            generated.append(data_runs[:, 1].mean())
            received.append(data_runs[:, 0].mean())
    return received, generated, devices


# Load data
runs = [0, 1]
devices_num = range(1, 4001, 10)
rxed_dr0_pl10, gen_dr0_pl10, devices_dr0_pl10 = get_rxed_gen_devices('results/dr0/pl10/', devices_num, runs)
rxed_dr0_pl50, gen_dr0_pl50, devices_dr0_pl50 = get_rxed_gen_devices('results/dr0/pl50/', devices_num, runs)
rxed_dr8_pl10, gen_dr8_pl10, devices_dr8_pl10 = get_rxed_gen_devices('results/dr8/pl10/', devices_num, runs)
# rxed_dr8_pl50, gen_dr8_pl50, devices_dr8_pl50 = get_rxed_gen_devices('results/dr8/pl50/', devices_num, runs)

# Fast check
plt.plot(devices_dr8_pl10, np.array(rxed_dr8_pl10) * np.array(devices_dr8_pl10))
plt.show()

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig = plt.figure()
plt.plot(devices_dr8_pl10, np.array(rxed_dr8_pl10) * np.array(devices_dr8_pl10), label=r'LoRa--E DR8 10B', linewidth=3.0, c='k', linestyle='-')
# plt.plot(devices_dr8_pl50, np.array(rxed_dr8_pl50) * np.array(devices_dr8_pl50), label=r'LoRa--E DR8 50B', linewidth=3.0, c='k', linestyle='--')
plt.plot(devices_dr0_pl10, np.array(rxed_dr0_pl10) * np.array(devices_dr0_pl10), label=r'LoRa DR0 10B', linewidth=3.0, c='grey', linestyle='-')
plt.plot(devices_dr0_pl50, np.array(rxed_dr0_pl50) * np.array(devices_dr0_pl50), label=r'LoRa DR0 50B', linewidth=3.0, c='grey', linestyle='--')
plt.xlabel(r'Number of end-devices', fontsize=16)
plt.ylabel(r'Received frames/hour', fontsize=16)
plt.legend(fontsize=14)     # loc=(0.62, 0.78)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title(r'1\% Duty cycle', fontsize=16)
plt.grid(linestyle='-.')
plt.xlim(0, 381)
# plt.yscale('log')
plt.show()
fig.savefig('./results/images/rxed_devices.png', format='png', dpi=300)

