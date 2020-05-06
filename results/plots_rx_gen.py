import matplotlib.pyplot as plt
import numpy as np


# # ------------------------------------------
# Generated vs Received
# 100 devices
def get_rxed_gen_lambda(_path, _tx_intervals, _runs):
    generated = []
    received = []
    for interval in _tx_intervals:
        data_runs = np.zeros((len(runs), 2), dtype=float)
        for run in _runs:
            data_runs[run] = np.load(_path + str(interval) + '_' + str(run) + '.npy')
        generated.append(data_runs[:, 1].mean())
        received.append(data_runs[:, 0].mean())
    return received, generated


# Lambdas of lora limit paper
# lambda = events/interval * interval length
# 0.1% DCC 10B pl is 36 packets hour in avg for SF 12 (lambd = 36)
lambd = np.arange(10, 1000, 100)
# Conversion to transmission interval in simulation units (ms)
tx_intervals = np.round(1./lambd * 3600000).astype(int)     # [360000, 32727, 17143, 11613, 8780, 7059, 5902, 5070, 4444, 3956]

# Load data
runs = [0, 1]
rxed_dr8, gen_dr8 = get_rxed_gen_lambda('results/dr8/100_', tx_intervals, runs)
rxed_dr5, gen_dr5 = get_rxed_gen_lambda('results/dr5/100_', tx_intervals, runs)
rxed_dr0, gen_dr0 = get_rxed_gen_lambda('results/dr0/100_', tx_intervals, runs)

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
fig = plt.figure()
plt.plot(gen_dr8, rxed_dr8, label=r'LoRa--E DR8', linewidth=3.0, c='k')
plt.plot(gen_dr5, rxed_dr5, label=r'LoRa DR5', linewidth=3.0, c='grey')
plt.plot(gen_dr0, rxed_dr0, label=r'LoRa DR0', linewidth=3.0, c='lightblue')
plt.xlabel(r'Generated frames/hour per node ($\lambda$)', fontsize=16)
plt.ylabel(r'Received frames/hour per node', fontsize=16)
plt.legend(fontsize=14)     # loc=(0.62, 0.78)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title(r'100 devices and 10B payload', fontsize=16)
plt.grid(linestyle='-.')
#plt.ylim(0, 300)
plt.show()
fig.savefig('./results/images/rxed_gen.png', format='png', dpi=300)

