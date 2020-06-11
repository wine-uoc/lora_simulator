import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})


lora = [7, 8, 9, 10, 11, 12]
lora = [5, 4, 3, 2, 1, 0]
devices_dr8_pl50 = [276, 246, 213, 181, 141, 116]
devices_dr9_pl50 = [184, 155, 124, 93, 55, 26]
devices_dr8_pl10 = [267, 245, 211, 175, 139, 114]
devices_dr9_pl10 = [179, 155, 119, 85, 50, 22]

mkr = ['s', 's', 'o', 'o']
clr = ['darkgrey', 'grey', 'dimgrey', 'k']

# The plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig = plt.figure()
#fig.tight_layout()
plt.plot(lora, devices_dr8_pl10, label=r'LoRa--E DR8 (10 bytes)', markersize=10, linewidth=2.5, c=clr[1], marker=mkr[2])
plt.plot(lora, devices_dr8_pl50, label=r'LoRa--E DR8 (50 bytes)', markersize=10, linewidth=2.5, c=clr[0], marker=mkr[0])
plt.plot(lora, devices_dr9_pl10, label=r'LoRa--E DR9 (10 bytes)', markersize=10, linewidth=2.5, c=clr[3], marker=mkr[3])
plt.plot(lora, devices_dr9_pl50, label=r'LoRa--E DR9 (50 bytes)', markersize=10, linewidth=2.5, c=clr[2], marker=mkr[1], alpha=0.8)
plt.ylabel(r'Number of end-devices', fontsize=16)
plt.xlabel(r'LoRa configuration', fontsize=16)
#plt.legend(fontsize=14)
plt.legend(fontsize=12, loc='lower left', bbox_to_anchor=(0, 1.05, 1, 0.2), ncol=2, borderaxespad=0)
plt.xticks(lora, ['DR5', 'DR4', 'DR3', 'DR2', 'DR1', 'DR0'], fontsize=14)
plt.yticks(range(20, 300, 20), fontsize=14)
plt.grid(linestyle='-.', which='both')
#plt.minorticks_on()
# plt.title(r'1\% Duty cycle', fontsize=16)
# plt.xlim(0, 400)
# plt.ylim(0, 200000)
fig.savefig('./results/images/plot_ferran.png', format='png', dpi=300)
#plt.yscale('log')
plt.show()
