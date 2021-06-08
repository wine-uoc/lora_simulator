"""
This generates the Time on Air plot, Lambda plot, and TOA vs lambda plot
"""
import matplotlib.pyplot as plt

import DeviceHelper


def get_toa(_dr, _pl):
    if _dr < 8:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora(_pl, _dr)
        reps = 1
    elif _dr == 8 or _dr == 10:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 162)
        reps = 3
    elif _dr == 9 or _dr == 11:
        t_preamble, t_payload = DeviceHelper.DeviceHelper.toa_lora_e(_pl, 366)
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
        toa_pl.append(toa/1000.)    # sec
        toff = DeviceHelper.DeviceHelper.get_off_period(toa, 0.01)  # dc 1%
        tx_inteval = (toa + toff) / 1000.
        lmbda_pl.append((3600./tx_inteval))
    toa_dr.append(toa_pl)
    lmbda_dr.append(lmbda_pl)
    del toa_pl, lmbda_pl


# The Time on Air plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

mkr = ['o', 'v', 's', 'd']
lgd = ['LoRa DR0', 'LoRa DR5', 'LoRa--E DR8/10', 'LoRa--E DR9/11']
clr = ['grey', 'grey', 'k', 'k']

fig = plt.figure()
for i in range(len(toa_dr)):
    plt.plot(pls, toa_dr[i], label=r'DR'+str(drs[i]), markersize=10, linewidth=3.0, c=clr[i], marker=mkr[i])
plt.xlabel(r'MAC payload size (Bytes)', fontsize=16)
plt.ylabel(r'Time on Air (sec)', fontsize=16)
plt.legend(lgd, fontsize=14)     # loc=(0.62, 0.78)
plt.xticks(pls, fontsize=14)
plt.yticks(fontsize=14)
plt.grid(linestyle='-.')
plt.xlim(10, 50)
plt.ylim(0, 6)
# plt.axes().set_aspect('auto')
fig.savefig('./results/images/toa.png', format='png', dpi=300)
plt.show()


# The Lambda plot
fig = plt.figure()
for i in range(len(toa_dr)):
    plt.plot(pls, lmbda_dr[i], label=r'DR'+str(drs[i]), markersize=10, linewidth=3.0, c=clr[i], marker=mkr[i])
plt.xlabel(r'MAC payload size (Bytes)', fontsize=16)
plt.ylabel(r'Maximum frames/hour per node ($\lambda$)', fontsize=16)
plt.title(r'Duty cycle 1\%', fontsize=16)
plt.legend(lgd, fontsize=14)     # loc=(0.62, 0.78)
plt.xticks(pls, fontsize=14)
plt.yticks(fontsize=14)
plt.grid(linestyle='-.')
plt.yscale('log')
plt.xlim(10, 50)
plt.ylim(0, 1000)
# plt.axes().set_aspect('auto')
fig.savefig('./results/images/lambda.png', format='png', dpi=300)
plt.show()


# The TOA vs lambda plot
fig = plt.figure()
for i in range(len(mkr)):
    if i > 1:
        color = 'k'
    else:
        color = 'grey'
    plt.scatter(lmbda_dr[0][-1], toa_dr[0][-1], s=80, marker=mkr[i], c=color, label=lgd[i])

mkr = ['o', 'v', 's', 'd']
for dr in range(len(drs)):
    if dr > 1:
        color = 'k'
    else:
        color = 'grey'
    for i in range(len(pls)):
        plt.plot(lmbda_dr[dr][i], toa_dr[dr][i], markersize=5+2*i, marker=mkr[dr], c=color)

plt.xlabel(r'Maximum frames/hour per node ($\lambda$) DC 1\%', fontsize=16)
plt.ylabel(r'Time on Air (sec)', fontsize=16)
plt.xscale('log')
plt.xlim(0, 1000)
plt.ylim(0, 5)
plt.legend(fontsize=16)     # loc=(0.62, 0.78)
plt.grid(linestyle='-.')
fig.savefig('./results/images/toalmbd.png', format='png', dpi=300)
plt.show()
