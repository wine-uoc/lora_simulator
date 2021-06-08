import matplotlib.pyplot as plt
import numpy as np


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
dvs = [100, 1000, 3000, 5000]
lmbd = np.arange(1, 900, 2)
tx_intervals = list(np.round(1. / lmbd * 3600000).astype(int))

# Load data
runs = [0, 1]
rxed_dr8, gen_dr8, lmbd_dr8 = get_rxed_gen_lambda('results/dr8/pl10/', tx_intervals, runs, dvs[-1], 8)
rxed_dr9, gen_dr9, lmbd_dr9 = get_rxed_gen_lambda('results/dr9/pl10/', tx_intervals, runs, dvs[-1], 9)
rxed_dr0, gen_dr0, lmbd_dr0 = get_rxed_gen_lambda('results/dr0/pl10/', tx_intervals, runs, dvs[-1], 0)

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig = plt.figure()
plt.plot(lmbd_dr9, rxed_dr9, label=r'LoRa--E DR9', linewidth=3.0, c='k', linestyle='-')
plt.plot(lmbd_dr8, rxed_dr8, label=r'LoRa--E DR8', linewidth=3.0, c='grey', linestyle='-')
plt.plot(lmbd_dr0, rxed_dr0, label=r'LoRa SF12', linewidth=3.0, c='silver')
plt.xlabel(r'Generated packets/hour/node ($\lambda$)', fontsize=16)
plt.ylabel(r'Received packets/hour', fontsize=16)
plt.legend(fontsize=14)  # loc=(0.62, 0.78)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# plt.title(r'10B payload', fontsize=16)
plt.grid(linestyle=':')
# plt.yscale('log')
# plt.xlim(1, 36)
plt.show()
#fig.savefig('./results/images/rxed_gen.png', format='png', dpi=300)
