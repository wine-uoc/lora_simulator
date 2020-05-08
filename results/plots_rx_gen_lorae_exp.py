import matplotlib.colors
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
dvs = [1000, 100, 10]
colors = ['k', 'grey', 'silver']
lmbd = np.arange(1, 900, 2)
tx_intervals = list(np.round(1. / lmbd * 3600000).astype(int))
runs = [0, 1]

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig = plt.figure()

# dummy for legend
plt.plot(0, 0, label=r'LoRa SF12', c='k', linestyle=':', linewidth=2.0)
plt.plot(0, 0, label=r'LoRa SF7', c='k', linestyle='-.', linewidth=2.0)
plt.plot(0, 0, label=r'LoRa--E DR8', c='k', linestyle='--', linewidth=2.0)
plt.plot(0, 0, label=r'LoRa--E DR9', c='k', linestyle='-', linewidth=2.0)

# colorbar
# https://stackoverflow.com/questions/8342549/matplotlib-add-colorbar-to-a-sequence-of-line-plots
n_lines = 3
c = np.arange(1., n_lines + 1)
cmap = plt.get_cmap("binary", len(c))
cmaplist = [cmap(i) for i in range(cmap.N)]
cmaplist[0] = (0.9, 0.9, 0.9, 1.0)  # force the first color entry to be grey
cmap = matplotlib.colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, cmap.N)     # create the new map
norm = matplotlib.colors.BoundaryNorm(np.arange(len(c)+1)+0.5, len(c))
sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

for i in range(len(dvs)):
    rxed_dr0, gen_dr0, lmbd_dr0 = get_rxed_gen_lambda('results/dr0/pl10/', tx_intervals, runs, dvs[i], 0)
    plt.plot(gen_dr0, rxed_dr0, linewidth=3.0, c=colors[i], linestyle=':')  # , label=r'DR0 N=' + str(dvs[i])
dvs2 = [900, 100, 0]
for i in range(len(dvs2)):
    rxed_dr5, gen_dr5, lmbd_dr5 = get_rxed_gen_lambda('results/dr5/pl10/', [360000, 32727, 17143, 11613, 8780, 7059, 5902, 5070, 4444, 3956], runs, dvs2[i], 5)
    plt.plot(gen_dr5, rxed_dr5, linewidth=3.0, c=colors[i], linestyle='-.')
for i in range(len(dvs)):
    rxed_dr8, gen_dr8, lmbd_dr8 = get_rxed_gen_lambda('results/dr8/pl10/', tx_intervals, runs, dvs[i], 8)
    plt.plot(gen_dr8, rxed_dr8, linewidth=3.0, c=colors[i], linestyle='--')
for i in range(len(dvs)):
    rxed_dr9, gen_dr9, lmbd_dr9 = get_rxed_gen_lambda('results/dr9/pl10/', tx_intervals, runs, dvs[i], 9)
    plt.plot(gen_dr9, rxed_dr9, linewidth=3.0, c=colors[i], linestyle='-')

plt.xlabel(r'Generated packets/hour', fontsize=16)
plt.ylabel(r'Received packets/hour', fontsize=16)
plt.legend(fontsize=12, loc='upper left')  # loc=(0.62, 0.78)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# plt.title(r'LoRa--E DR8 10B payload', fontsize=16)
plt.grid(linestyle=':', which='both')
plt.yscale('log')
plt.xscale('log')
plt.xlim(10, 1000000)
plt.ylim(10, 1000000)
cbar = fig.colorbar(sm, ticks=c, orientation='horizontal', aspect=45, pad=0.18)
cbar.ax.set_xticklabels([r'10 devices', r'100 devices', r'1000 devices'], fontsize=14)  # horizontal colorbar
fig.savefig('./results/images/rxed_gen_exp.png', format='png', dpi=300)
plt.show()
