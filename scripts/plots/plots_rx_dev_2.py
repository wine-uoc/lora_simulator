import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

import LoraHelper

rcParams.update({'figure.autolayout': True})
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.viridis(np.linspace(0, 1, 6)))  # 6: num of LORA DRs


# ------------------------------------------
# Received vs number of devices
# Maximum transmission rate

def get_toa(_dr, _pl):
    if _dr < 8:
        t_preamble, t_payload = LoraHelper.LoraHelper.toa_lora(_pl, _dr)
        reps = 1
    elif _dr == 8 or _dr == 10:
        t_preamble, t_payload = LoraHelper.LoraHelper.toa_lora_e(_pl, 162)
        reps = 3
    elif _dr == 9 or _dr == 11:
        t_preamble, t_payload = LoraHelper.LoraHelper.toa_lora_e(_pl, 325)
        reps = 2
    else:
        print('Unknown')
        return 0.
    return reps * t_preamble + t_payload


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
pl_size = 10
runs = range(10)
devices_num = range(1, 911, 10)
rxed_dr0, gen_dr0, devices_dr0 = get_rxed_gen_devices('results/dr0/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr1, gen_dr1, devices_dr1 = get_rxed_gen_devices('results/dr1/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr2, gen_dr2, devices_dr2 = get_rxed_gen_devices('results/dr2/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr3, gen_dr3, devices_dr3 = get_rxed_gen_devices('results/dr3/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr4, gen_dr4, devices_dr4 = get_rxed_gen_devices('results/dr4/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr5, gen_dr5, devices_dr5 = get_rxed_gen_devices('results/dr5/pl' + str(pl_size) + '/', devices_num, runs)
devices_num = [1, 11, 101, 201, 401, 601, 801, 1001, 1251, 1501, 1751, 2001, 2251, 2501, 2751, 3001, 3501, 4000, 4500,
               5000, 6000, 7000, 8000, 10000]
# devices_num = [1, 11, 101, 201, 401, 601, 801, 1001, 1501, 2001, 2501, 3001, 3501, 4000, 4500, 5000, 5500, 6000,
#                6500, 7000, 7500, 8000, 10000, 12500, 15000, 17500, 20000]
rxed_dr8, gen_dr8, devices_dr8 = get_rxed_gen_devices('results/dr8/pl' + str(pl_size) + '/', devices_num, runs)
rxed_dr9, gen_dr9, devices_dr9 = get_rxed_gen_devices('results/dr9/pl' + str(pl_size) + '/', devices_num, runs)

# Metric to plot in Y-axis
metric = 'goodput'
lora_cr_factor = 4 / 5
dr8_cr_factor = 1 / 3
dr9_cr_factor = 2 / 3
time_factor = 1
metric_dr0 = np.array(rxed_dr0) * np.array(devices_dr0) * pl_size * lora_cr_factor / time_factor
metric_dr1 = np.array(rxed_dr1) * np.array(devices_dr1) * pl_size * lora_cr_factor / time_factor
metric_dr2 = np.array(rxed_dr2) * np.array(devices_dr2) * pl_size * lora_cr_factor / time_factor
metric_dr3 = np.array(rxed_dr3) * np.array(devices_dr3) * pl_size * lora_cr_factor / time_factor
metric_dr4 = np.array(rxed_dr4) * np.array(devices_dr4) * pl_size * lora_cr_factor / time_factor
metric_dr5 = np.array(rxed_dr5) * np.array(devices_dr5) * pl_size * lora_cr_factor / time_factor
metric_dr8 = np.array(rxed_dr8) * np.array(devices_dr8) * pl_size * dr8_cr_factor / time_factor
metric_dr9 = np.array(rxed_dr9) * np.array(devices_dr9) * pl_size * dr9_cr_factor / time_factor
y_label = r'Goodput (bytes/hour)'

# Metric to plot in X-axis
metric_dr0_x = np.array(devices_dr0) * 3600. / ((get_toa(0, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(0, pl_size), 0.01)) / 1000.)
metric_dr1_x = np.array(devices_dr1) * 3600. / ((get_toa(1, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(1, pl_size), 0.01)) / 1000.)
metric_dr2_x = np.array(devices_dr2) * 3600. / ((get_toa(2, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(2, pl_size), 0.01)) / 1000.)
metric_dr3_x = np.array(devices_dr3) * 3600. / ((get_toa(3, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(3, pl_size), 0.01)) / 1000.)
metric_dr4_x = np.array(devices_dr4) * 3600. / ((get_toa(4, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(4, pl_size), 0.01)) / 1000.)
metric_dr5_x = np.array(devices_dr5) * 3600. / ((get_toa(5, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(5, pl_size), 0.01)) / 1000.)
metric_dr8_x = np.array(devices_dr8) * 3600. / ((get_toa(8, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(8, pl_size), 0.01)) / 1000.)
metric_dr9_x = np.array(devices_dr9) * 3600. / ((get_toa(9, pl_size) + LoraHelper.LoraHelper.get_off_period(get_toa(9, pl_size), 0.01)) / 1000.)
x_label = r'Generated packets per hour'


# The plot
fig = plt.figure()
plt.plot(metric_dr0_x[:-18], metric_dr0[:-18], label=r'LoRa DR0 (SF12)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr1_x[:-18], metric_dr1[:-18], label=r'LoRa DR1 (SF11)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr2_x, metric_dr2, label=r'LoRa DR2 (SF10)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr3_x[:-8], metric_dr3[:-8], label=r'LoRa DR3 (SF9)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr4_x, metric_dr4, label=r'LoRa DR4 (SF8)', linewidth=3.0, linestyle=':')
plt.plot(metric_dr5_x, metric_dr5, label=r'LoRa DR5 (SF7)', linewidth=3.0, linestyle=':')
plt.plot(np.concatenate((metric_dr8_x[:1], metric_dr8_x * 8.)),
         np.concatenate((metric_dr8[:1], metric_dr8 * 8.)), label=r'LoRa--E DR8', linewidth=3.0,
         c='grey', linestyle='-')
plt.plot(np.concatenate((metric_dr9_x[:1], metric_dr9_x * 8.)),
         np.concatenate((metric_dr9[:1], metric_dr9 * 8.)), label=r'LoRa--E DR9', linewidth=3.0,
         c='k', linestyle='-')
plt.xlabel(x_label, fontsize=16)
plt.ylabel(y_label, fontsize=16)
plt.legend(fontsize=10, ncol=3, loc='lower right', framealpha=1)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(linestyle='-.', which='both')
plt.xlim(100, 2000000)
plt.ylim(100, 2000000)
plt.yscale('log')
plt.xscale('log')
#fig.savefig('images/rxed_devices_generated_pl' + str(pl_size) + '_new.png', format='png', dpi=300)
plt.show()
plt.close()
