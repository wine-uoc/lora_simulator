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
runs = range(10)
devices_num = range(1, 1011, 10)
rxed_dr0_pl10, gen_dr0_pl10, devices_dr0_pl10 = get_rxed_gen_devices('results/dr0/pl10/', devices_num, runs)
rxed_dr1_pl10, gen_dr1_pl10, devices_dr1_pl10 = get_rxed_gen_devices('results/dr1/pl10/', devices_num, runs)
rxed_dr2_pl10, gen_dr2_pl10, devices_dr2_pl10 = get_rxed_gen_devices('results/dr2/pl10/', devices_num, runs)
rxed_dr3_pl10, gen_dr3_pl10, devices_dr3_pl10 = get_rxed_gen_devices('results/dr3/pl10/', devices_num, runs)
rxed_dr4_pl10, gen_dr4_pl10, devices_dr4_pl10 = get_rxed_gen_devices('results/dr4/pl10/', devices_num, runs)
rxed_dr5_pl10, gen_dr5_pl10, devices_dr5_pl10 = get_rxed_gen_devices('results/dr5/pl10/', devices_num, runs)
devices_num = [1, 11, 101, 201, 401, 601, 801, 1001, 1501, 2001, 2501, 3001, 3501, 4000, 4500, 5000, 5500, 6000,
               6500, 7000, 7500, 8000, 10000]
rxed_dr8_pl10, gen_dr8_pl10, devices_dr8_pl10 = get_rxed_gen_devices('results/dr8/pl10/', devices_num, runs)
rxed_dr9_pl10, gen_dr9_pl10, devices_dr9_pl10 = get_rxed_gen_devices('results/dr9/pl10/', devices_num, runs)

# Metric to plot in Y-axis
metric = 1
if metric == 1:
    # Goodput
    y_label = 'Goodput (bytes/hour)'
    lora_cr_factor = 4 / 5
    dr8_cr_factor = 1 / 3
    dr9_cr_factor = 2 / 3
    time_factor = 1
    metric_dr0_pl10 = rxed_dr0_pl10 * devices_dr0_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr1_pl10 = rxed_dr1_pl10 * devices_dr1_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr2_pl10 = rxed_dr2_pl10 * devices_dr2_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr3_pl10 = rxed_dr3_pl10 * devices_dr3_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr4_pl10 = rxed_dr4_pl10 * devices_dr4_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr5_pl10 = rxed_dr5_pl10 * devices_dr5_pl10 * 10 * lora_cr_factor / time_factor
    metric_dr8_pl10 = rxed_dr8_pl10 * devices_dr8_pl10 * 10 * dr8_cr_factor / time_factor
    metric_dr9_pl10 = rxed_dr9_pl10 * devices_dr9_pl10 * 10 * dr9_cr_factor / time_factor
elif metric == 2:
    # PDR
    y_label = r'PDR'
    metric_dr0_pl10 = rxed_dr0_pl10 / gen_dr0_pl10
    metric_dr1_pl10 = rxed_dr1_pl10 / gen_dr1_pl10
    metric_dr2_pl10 = rxed_dr2_pl10 / gen_dr2_pl10
    metric_dr3_pl10 = rxed_dr3_pl10 / gen_dr3_pl10
    metric_dr4_pl10 = rxed_dr4_pl10 / gen_dr4_pl10
    metric_dr5_pl10 = rxed_dr5_pl10 / gen_dr5_pl10
    metric_dr8_pl10 = rxed_dr8_pl10 / gen_dr8_pl10
    metric_dr9_pl10 = rxed_dr9_pl10 / gen_dr9_pl10
elif metric == 3:
    # PER
    y_label = r'PER'
    metric_dr0_pl10 = 1 - rxed_dr0_pl10 / gen_dr0_pl10
    metric_dr1_pl10 = 1 - rxed_dr1_pl10 / gen_dr1_pl10
    metric_dr2_pl10 = 1 - rxed_dr2_pl10 / gen_dr2_pl10
    metric_dr3_pl10 = 1 - rxed_dr3_pl10 / gen_dr3_pl10
    metric_dr4_pl10 = 1 - rxed_dr4_pl10 / gen_dr4_pl10
    metric_dr5_pl10 = 1 - rxed_dr5_pl10 / gen_dr5_pl10
    metric_dr8_pl10 = 1 - rxed_dr8_pl10 / gen_dr8_pl10
    metric_dr9_pl10 = 1 - rxed_dr9_pl10 / gen_dr9_pl10
elif metric == 4:
    # RXED 
    y_label = r'RXED packets'
    metric_dr0_pl10 = rxed_dr0_pl10 * devices_dr0_pl10
    metric_dr1_pl10 = rxed_dr1_pl10 * devices_dr1_pl10
    metric_dr2_pl10 = rxed_dr2_pl10 * devices_dr2_pl10
    metric_dr3_pl10 = rxed_dr3_pl10 * devices_dr3_pl10
    metric_dr4_pl10 = rxed_dr4_pl10 * devices_dr4_pl10
    metric_dr5_pl10 = rxed_dr5_pl10 * devices_dr5_pl10
    metric_dr8_pl10 = rxed_dr8_pl10 * devices_dr8_pl10
    metric_dr9_pl10 = rxed_dr9_pl10 * devices_dr9_pl10
    pass
elif metric == 6:
    pass

# Metric to plot in X-axis
metric = 1
if metric == 4:
    # TXED
    x_label = r'TXED packets'
    metric_dr0_x = gen_dr0_pl10 * devices_dr0_pl10
    metric_dr1_x = gen_dr1_pl10 * devices_dr1_pl10
    metric_dr2_x = gen_dr2_pl10 * devices_dr2_pl10
    metric_dr3_x = gen_dr3_pl10 * devices_dr3_pl10
    metric_dr4_x = gen_dr4_pl10 * devices_dr4_pl10
    metric_dr5_x = gen_dr5_pl10 * devices_dr5_pl10
    metric_dr8_x = gen_dr8_pl10 * devices_dr8_pl10
    metric_dr9_x = gen_dr9_pl10 * devices_dr9_pl10
else:
    x_label = r'Number of end-devices'
    metric_dr0_x = devices_dr0_pl10
    metric_dr1_x = devices_dr1_pl10
    metric_dr2_x = devices_dr2_pl10
    metric_dr3_x = devices_dr3_pl10
    metric_dr4_x = devices_dr4_pl10
    metric_dr5_x = devices_dr5_pl10
    metric_dr8_x = devices_dr8_pl10
    metric_dr9_x = devices_dr9_pl10

# The plot
fig = plt.figure()
plt.plot(metric_dr0_x, metric_dr0_pl10, label=r'LoRa DR0 (SF12)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr1_x, metric_dr1_pl10, label=r'LoRa DR1 (SF11)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr2_x, metric_dr2_pl10, label=r'LoRa DR2 (SF10)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr3_x, metric_dr3_pl10, label=r'LoRa DR3 (SF9)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr4_x, metric_dr4_pl10, label=r'LoRa DR4 (SF8)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr5_x, metric_dr5_pl10, label=r'LoRa DR5 (SF7)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr8_x, metric_dr8_pl10, label=r'LoRa--E DR8', linewidth=3.0, c='grey', linestyle='-')
plt.plot(metric_dr9_x, metric_dr9_pl10, label=r'LoRa--E DR9', linewidth=3.0, c='k', linestyle='-')
plt.xlabel(x_label, fontsize=16)
plt.ylabel(y_label, fontsize=16)
# plt.legend(fontsize=10, ncol=3, loc='upper right', framealpha=1)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(linestyle='-.', which='both')
# plt.xlim(1, 150)
# plt.axhline(y=0.184, color='blue', linestyle=':')
# plt.axhline(y=0.184*2, color='green', linestyle=':')
# plt.axvline(x=51, color='green', linestyle=':')
a = plt.scatter(1843.9, 679.7, c='red')
b = plt.scatter(43674.0, 16132.9, c='blue')
plt.legend([a, b], ['txed = 1843.9, rxed = 679.7, pdr = 0.368', 'txed = 43674.0, rxed = 16132.9, pdr = 0.369'])
# plt.ylim(10, 1000)
plt.yscale('log')
plt.xscale('log')
plt.show()


# ------------------------------------------------------------
# get the Max values
def _get_devs_max_metric(metric_arr, devs_array):
    idx = np.where(metric_arr == max(metric_arr))[0][0]
    return max(metric_arr), devs_array[idx], idx


# rxed max. and devices that produced the max
_get_devs_max_metric(metric_dr0_pl10, devices_dr0_pl10)

# rxed max. and txed that produced the max
_get_devs_max_metric(metric_dr0_pl10, metric_dr0_x)

# same
_get_devs_max_metric(metric_dr5_pl10, devices_dr5_pl10)
_get_devs_max_metric(metric_dr5_pl10, metric_dr5_x)

np.argwhere()