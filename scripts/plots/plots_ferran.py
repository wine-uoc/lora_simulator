import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})


lora = [7, 8, 9, 10, 11, 12]
lora = [5, 4, 3, 2, 1, 0]
devices_dr8_pl50 = [270, 240, 208, 177, 138, 112]
devices_dr9_pl50 = [183, 154, 122, 92, 54, 25]
devices_dr8_pl10 = [247, 224, 188, 155, 120, 92]
devices_dr9_pl10 = [171, 146, 111, 76, 41, 14]
y_label = r'Number of end-devices'

devices_dr8_pl50 = [34600, 19000, 9725, 5125, 2400, 1400]
devices_dr9_pl50 = [14000, 7775, 4000, 2020, 900, 500]
devices_dr8_pl10 = [68000, 38750, 19450, 9650, 4850, 2800]
devices_dr9_pl10 = [23000, 13400, 6650, 3210, 1655, 985]
y_label = r'Packets generated per hour'

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
plt.ylabel(y_label, fontsize=16)
plt.xlabel(r'LoRa configuration', fontsize=16)
#plt.legend(fontsize=14)
plt.legend(fontsize=12, loc='lower left', bbox_to_anchor=(0, 1.05, 1, 0.2), ncol=2, borderaxespad=0)
plt.xticks(lora, ['DR5', 'DR4', 'DR3', 'DR2', 'DR1', 'DR0'], fontsize=14)
#plt.yticks(range(20, 300, 20), fontsize=14)
plt.grid(linestyle='-.', which='both')
#plt.minorticks_on()
# plt.title(r'1\% Duty cycle', fontsize=16)
# plt.xlim(0, 400)
plt.ylim(4*10**2, 10**5)
plt.yscale('log')
fig.savefig('./images/plot_ferran_log.png', format='png', dpi=300)
plt.show()
