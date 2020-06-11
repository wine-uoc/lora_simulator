import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})


# # ------------------------------------------
# Generated vs Received


def get_rxed_gen_lambda(_path, _tx_intervals, _runs, _num_devs, _dr):
    _path = _path + str(_num_devs) + '_'
    generated = []
    received = []
    intervals = []
    for interval in _tx_intervals:
        data_runs = np.zeros((len(runs), 2), dtype=float)
        for run in _runs:
            try:
                full_path = _path + str(interval) + '_' + str(run) + '.npy'
                data_runs[run] = np.load(full_path)
                print(full_path)
                skip = False
            except:
                skip = True
        if not skip:
            intervals.append(interval)
            generated.append(data_runs[:, 1].mean())
            received.append(data_runs[:, 0].mean())
    try:
        if _dr == 0:
            interval = 98132
        elif _dr == 8:
            interval = 267667
        elif _dr == 9:
            interval = 0
        else:
            pass
        for run in _runs:
            data_runs[run] = np.load('results/dr' + str(_dr) + '/pl10/' + str(_num_devs) + '_' + str(interval) + '_' + str(run) + '.npy')
        intervals.append(interval)
        generated.append(data_runs[:, 1].mean())
        received.append(data_runs[:, 0].mean())
    except:
        print('Last not found')

    return np.array(received) * _num_devs, np.array(generated) * _num_devs, 3600000. / np.array(intervals)


# Sim param
dvs = [100, 1000, 3000, 5000]  # not showing 10 devices, irrelevant
lmbd = np.arange(1, 50, 2)
tx_intervals = list(np.round(1. / lmbd * 3600000).astype(int))
runs = [0, 1]

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
colors = ['lightgrey', 'darkgrey', 'dimgrey', 'k']
red_patch = mpatches.Patch(color='red', alpha=0.1, label=r'Not received')

fig = plt.figure()
for i in range(len(dvs)):
    rxed_dr8, gen_dr8, lmbd_dr8 = get_rxed_gen_lambda('results/dr8/pl10/', tx_intervals, runs, dvs[i], 8)
    # plt.axhline(y=max(gen_dr8), color='blue', linestyle=':')
    if len(lmbd_dr8) > 0:
        plt.plot(lmbd_dr8, np.array(lmbd_dr8) * dvs[i], c=colors[i], linestyle='--')
        plt.plot(lmbd_dr8, rxed_dr8, label=str(dvs[i]) + r' devices', linewidth=3.0, c=colors[i], linestyle='-')
        plt.fill_between(lmbd_dr8, rxed_dr8, np.array(lmbd_dr8) * dvs[i], color='red', alpha=0.1)

# plt.plot(0, 0, label=r'PDR=1', linewidth=2., color='blue', linestyle=':')
plt.plot(0, 0, label=r'Lost packets', linewidth=10., color='red', alpha=0.1, linestyle='--')
plt.xlabel(r'Generated packets/hour/device ($\lambda$)', fontsize=16)
plt.ylabel(r'Received packets/hour', fontsize=16)
plt.legend(fontsize=14)  # loc=(0.62, 0.78)
plt.xticks(range(1, 14, 2), fontsize=14)
plt.yticks(fontsize=14)
plt.title(r'LoRa--E DR8 10B payload', fontsize=16)
plt.grid(linestyle=':', which='both')
# plt.yscale('log')
plt.xlim(1, 13)
# plt.ylim(1, 100000)
# fig.savefig('./results/images/rxed_gen_dr8.png', format='png', dpi=300)
plt.show()
