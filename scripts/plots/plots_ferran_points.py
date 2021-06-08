import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
N = 6  # number of SFs of LoRa
plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.viridis(np.linspace(0, 1, N)))


# ------------------------------------------
# Received vs number of devices
# Maximum transmission rate
def get_rxed_gen_devices(_path, _devices_num, _runs):
    generated = []
    received = []
    devices = []
    for device in _devices_num:
        data_runs = np.empty((len(runs), 2), dtype=float)
        data_runs[:] = np.nan
        skip = 0
        for run in _runs:
            try:
                full_path = _path + str(device) + '_max_' + str(run) + '.npy'
                data_runs[run] = np.load(full_path)
                print(full_path)
            except:
                skip = skip + 1
        if skip < len(_runs):
            devices.append(device)
            generated.append(np.nanmean(data_runs[:, 1]))
            received.append(np.nanmean(data_runs[:, 0]))
    return np.array(received), np.array(generated), np.array(devices)


# Load data
pl_size = 10
runs = range(10)
devices_num = range(1, 911, 10)
rxed_dr0, gen_dr0, devices_dr0 = get_rxed_gen_devices('results/dr0/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr1, gen_dr1, devices_dr1 = get_rxed_gen_devices('results/dr1/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr2, gen_dr2, devices_dr2 = get_rxed_gen_devices('results/dr2/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr3, gen_dr3, devices_dr3 = get_rxed_gen_devices('results/dr3/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr4, gen_dr4, devices_dr4 = get_rxed_gen_devices('results/dr4/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr5, gen_dr5, devices_dr5 = get_rxed_gen_devices('results/dr5/pl' + str(pl_size) + '/', devices_num, runs)
devices_num = [1, 11, 101, 201, 401, 601, 801, 1001, 1501, 2001, 2501, 3001, 3501, 4000, 4500, 5000, 5500, 6000,
               6500, 7000, 7500, 8000, 10000]
rxed_dr8, gen_dr8, devices_dr8 = get_rxed_gen_devices('results/dr8/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr9, gen_dr9, devices_dr9 = get_rxed_gen_devices('results/dr9/pl' + str(pl_size) + '/', devices_num, runs)

# Goodput y-axis
y_label = 'Goodput (bytes/hour)'
lora_cr_factor = 4 / 5
dr8_cr_factor = 1 / 3
dr9_cr_factor = 2 / 3
time_factor = 1
metric_dr0 = rxed_dr0 * devices_dr0 * pl_size * lora_cr_factor / time_factor
metric_dr1 = rxed_dr1 * devices_dr1 * pl_size * lora_cr_factor / time_factor
metric_dr2 = rxed_dr2 * devices_dr2 * pl_size * lora_cr_factor / time_factor
metric_dr3 = rxed_dr3 * devices_dr3 * pl_size * lora_cr_factor / time_factor
metric_dr4 = rxed_dr4 * devices_dr4 * pl_size * lora_cr_factor / time_factor
metric_dr5 = rxed_dr5 * devices_dr5 * pl_size * lora_cr_factor / time_factor
metric_dr8 = rxed_dr8 * devices_dr8 * pl_size * dr8_cr_factor / time_factor
metric_dr9 = rxed_dr9 * devices_dr9 * pl_size * dr9_cr_factor / time_factor

# Devices x-axis
x_label = r'Number of end-devices'
metric_dr0_x = devices_dr0
metric_dr1_x = devices_dr1
metric_dr2_x = devices_dr2
metric_dr3_x = devices_dr3
metric_dr4_x = devices_dr4
metric_dr5_x = devices_dr5
metric_dr8_x = devices_dr8
metric_dr9_x = devices_dr9

# The plot
fig = plt.figure()
plt.plot(metric_dr0_x, metric_dr0, label=r'LoRa DR0 (SF12)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr1_x, metric_dr1, label=r'LoRa DR1 (SF11)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr2_x, metric_dr2, label=r'LoRa DR2 (SF10)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr3_x, metric_dr3, label=r'LoRa DR3 (SF9)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr4_x, metric_dr4, label=r'LoRa DR4 (SF8)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr5_x, metric_dr5, label=r'LoRa DR5 (SF7)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr8_x, metric_dr8, label=r'LoRa--E DR8', linewidth=3.0, c='grey', linestyle='-')
plt.plot(metric_dr9_x, metric_dr9, label=r'LoRa--E DR9', linewidth=3.0, c='k', linestyle='-')
plt.xlabel(x_label, fontsize=16)
plt.ylabel(y_label, fontsize=16)
# plt.legend(fontsize=10, ncol=3, loc='upper right', framealpha=1)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(linestyle='-.', which='both')
plt.minorticks_on()

# dr8 pl 10
devices_dr8 = [247, 224, 188, 155, 119, 92]
plt.xlim(187, 250)
plt.ylim(8000, 12000)

# dr 9 pl 10
devices_dr9 = [171, 146, 111, 76, 40, 14]
plt.xlim(110, 180)
plt.ylim(20000, 40000)

devices = devices_dr9
for i in range(len(devices)):
    plt.axvline(x=devices[i], color='red', linestyle=':')
#plt.yscale('log')
#plt.xscale('log')
plt.show()
plt.close()

