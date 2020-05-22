import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

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
    return received, generated, devices


# Load data
runs = range(10)
devices_num = range(1, 4001, 10)
# devices_num.extend([900, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000])

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

# rxed_dr0_pl50, gen_dr0_pl50, devices_dr0_pl50 = get_rxed_gen_devices('results/dr0/pl50/', devices_num, runs)
# rxed_dr5_pl50, gen_dr5_pl50, devices_dr5_pl50 = get_rxed_gen_devices('results/dr5/pl50/', devices_num, runs)

# Metric to plot
metric = 'goodput'
# if throughput, consider different header repetitions in dr 8 and 9
if metric == 'pkt/h':
    # metric_dr0_pl50 = np.array(rxed_dr0_pl50) * np.array(devices_dr0_pl50)
    metric_dr0_pl10 = np.array(rxed_dr0_pl10) * np.array(devices_dr0_pl10)
    metric_dr5_pl10 = np.array(rxed_dr5_pl10) * np.array(devices_dr5_pl10)
    metric_dr8_pl10 = np.array(rxed_dr8_pl10) * np.array(devices_dr8_pl10)
    metric_dr9_pl10 = np.array(rxed_dr9_pl10) * np.array(devices_dr9_pl10)
    y_label = r'Received packets/hour'
elif metric == 'goodput':
    lora_cr_factor = 4 / 5
    dr8_cr_factor = 1 / 3
    dr9_cr_factor = 2 / 3
    time_factor = 1
    metric_dr0_pl10 = np.array(rxed_dr0_pl10) * np.array(devices_dr0_pl10) * 10 * lora_cr_factor / time_factor
    metric_dr1_pl10 = np.array(rxed_dr1_pl10) * np.array(devices_dr1_pl10) * 10 * lora_cr_factor / time_factor
    metric_dr2_pl10 = np.array(rxed_dr2_pl10) * np.array(devices_dr2_pl10) * 10 * lora_cr_factor / time_factor
    metric_dr3_pl10 = np.array(rxed_dr3_pl10) * np.array(devices_dr3_pl10) * 10 * lora_cr_factor / time_factor
    metric_dr4_pl10 = np.array(rxed_dr4_pl10) * np.array(devices_dr4_pl10) * 10 * lora_cr_factor / time_factor
    metric_dr5_pl10 = np.array(rxed_dr5_pl10) * np.array(devices_dr5_pl10) * 10 * lora_cr_factor / time_factor

    metric_dr8_pl10 = np.array(rxed_dr8_pl10) * np.array(devices_dr8_pl10) * 10 * dr8_cr_factor / time_factor
    metric_dr9_pl10 = np.array(rxed_dr9_pl10) * np.array(devices_dr9_pl10) * 10 * dr9_cr_factor / time_factor

    # metric_dr0_pl50 = np.array(rxed_dr0_pl50) * np.array(devices_dr0_pl50) * 50 * lora_cr_factor / time_factor
    # metric_dr5_pl50 = np.array(rxed_dr5_pl50) * np.array(devices_dr5_pl50) * 50 * lora_cr_factor / time_factor

    y_label = r'Goodput (bytes/hour)'

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

N = 6
plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.viridis(np.linspace(0,1,N)))


fig = plt.figure()

# plt.plot(devices_dr0_pl50, metric_dr0_pl50, label=r'LoRa SF12 50B', linewidth=3.0, linestyle='--')
# plt.plot(devices_dr5_pl50, metric_dr5_pl50, label=r'LoRa SF7 50B', linewidth=3.0, linestyle='--')

plt.plot(devices_dr0_pl10, metric_dr0_pl10, label=r'LoRa DR0 (SF12)', linewidth=3.0, linestyle=':')
plt.plot(devices_dr1_pl10, metric_dr1_pl10, label=r'LoRa DR1 (SF11)', linewidth=3.0, linestyle=':')
plt.plot(devices_dr2_pl10, metric_dr2_pl10, label=r'LoRa DR2 (SF10)', linewidth=3.0, linestyle=':')
plt.plot(devices_dr3_pl10, metric_dr3_pl10, label=r'LoRa DR3 (SF9)', linewidth=3.0, linestyle=':')
plt.plot(devices_dr4_pl10, metric_dr4_pl10, label=r'LoRa DR4 (SF8)', linewidth=3.0, linestyle=':')
plt.plot(devices_dr5_pl10, metric_dr5_pl10, label=r'LoRa DR5 (SF7)', linewidth=3.0, linestyle=':')

plt.plot(devices_dr8_pl10, metric_dr8_pl10, label=r'LoRa--E DR8', linewidth=3.0, c='grey', linestyle='-')
plt.plot(devices_dr9_pl10, metric_dr9_pl10, label=r'LoRa--E DR9', linewidth=3.0, c='k', linestyle='-')
# plt.plot(devices_dr8_pl50, np.array(rxed_dr8_pl50) * np.array(devices_dr8_pl50), label=r'LoRa--E DR8 50B', linewidth=3.0, c='k', linestyle='--')
plt.xlabel(r'Number of end-devices', fontsize=16)
plt.ylabel(y_label, fontsize=16)
plt.legend(fontsize=10, ncol=3, loc='lower right', framealpha=1)     # loc=(0.62, 0.78)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
#plt.title(r'1\% Duty cycle', fontsize=16)
plt.grid(linestyle='-.', which='both')
plt.xlim(1, 10000)
plt.ylim(10, 1000000)
plt.yscale('log')
plt.xscale('log')
fig.savefig('./results/images/rxed_devices_goodp.png', format='png', dpi=300)
plt.show()

#
# devices_num = [1, 11, 101, 201, 401, 601, 801, 1001, 1501, 2001, 2501, 3001, 3501, 4000, 4500, 5000, 5500, 6000,
#                    6500, 7000, 7500, 8000, 10000]
# rxed_dr8_pl10, gen_dr8_pl10, devices_dr8_pl10 = get_rxed_gen_devices('results/dr8/pl10/', devices_num, runs)
# rxed_dr9_pl10, gen_dr9_pl10, devices_dr9_pl10 = get_rxed_gen_devices('results/dr9/pl10/', devices_num, runs)
