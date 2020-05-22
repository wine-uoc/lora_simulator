"""
This generates the TOA + lambda plot
"""
import matplotlib.pyplot as plt
from matplotlib import rcParams

import DeviceHelper

rcParams.update({'figure.autolayout': True})


def get_toa(_dr, _pl):
    if _dr < 8:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora(_pl, _dr)
        reps = 1
    elif _dr == 8 or _dr == 10:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 162)
        reps = 3
    elif _dr == 9 or _dr == 11:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 325)
        reps = 2
    else:
        print('Unknown')
        return 0.
    return reps * t_preamble + t_payload


pls = [10, 20, 30, 40, 50]
drs = [0, 5, 8, 9]

toa_dr = []
lmbda_dr = []
for dr in drs:
    toa_pl = []
    lmbda_pl = []
    for pl in pls:
        toa = get_toa(dr, pl)
        toa_pl.append(toa / 1000.)  # sec
        toff = DeviceHelper.DeviceHelper.get_off_period(toa, 0.01)  # dc 1%
        tx_inteval = (toa + toff) / 1000.
        lmbda_pl.append((3600. / tx_inteval))
    toa_dr.append(toa_pl)
    lmbda_dr.append(lmbda_pl)
    del toa_pl, lmbda_pl

# The Time on Air plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

mkr = ['o', 'v', 's', 'd']
lgd = ['LoRa DR0', 'LoRa DR5', 'LoRa--E DR8/10', 'LoRa--E DR9/11']
clr = ['grey', 'grey', 'k', 'k']


def plot_fig_1(_ax):
    for i in range(len(toa_dr)):
        _ax.plot(pls, toa_dr[i], markersize=8, linewidth=2.5, c=clr[i], marker=mkr[i])


def plot_fig_2(_ax):
    for i in range(len(toa_dr)):
        _ax.plot(pls, lmbda_dr[i], label=r'DR' + str(drs[i]), markersize=8, linewidth=2.5, c=clr[i], marker=mkr[i])


# The subplot
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()
plot_fig_1(ax1)
ax1.set_xticks([])
ax1.set_ylabel(r'Time on Air (sec)', fontsize=14)
ax1.set_yticks(range(6))
ax1.grid(linestyle=':', axis='y')
#ax1.set_xlim(10, 50)
ax1.set_ylim(0, 5)
ax1.tick_params(labelsize=12)
ax1.legend(lgd, fontsize=10, loc='lower left', bbox_to_anchor=(0, 1.10, 1, 0.2), ncol=4, mode="expand", borderaxespad=0)

plot_fig_2(ax2)
ax2.set_xticks(pls)
ax2.set_ylabel(r'Packets/hour/node', fontsize=14)
ax2.set_xlabel(r'MAC payload size (Bytes)', fontsize=14)
ax2.grid(linestyle=':', axis='y', which="both")
#ax2.set_xlim(10, 50)
ax2.set_ylim(7, 1000)
ax2.set_yscale('log')
ax2.tick_params(labelsize=14)
fig.savefig('./results/images/toa_lmbd.png', format='png', dpi=300)
plt.show()
