import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})

# load grid
dvs = np.load('scripts/plots/devices.npy', allow_pickle=True)
grid = np.load('scripts/plots/grid.npy', allow_pickle=True)

lora_pkt_t = 991
lora_pkt_start = 700
lora_pkt_end = lora_pkt_t + lora_pkt_start

# Latex
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# The plot
fig, ax = plt.subplots(1)
ax.plot(0, grid.shape[0])
ax.plot(3000, 0)
for device in dvs:
    pkts = device.pkt_list
    for pkt in pkts:
        start = pkt.start_time
        end = pkt.end_time
        freq = pkt.channel
        width = end - start
        if start >= lora_pkt_start - pkt.duration and end <= lora_pkt_end + pkt.duration:
            # overlap with SF12 pkt
            pkt.collided = 1
        if pkt.collided:
            color = 'red'
        else:
            height = 0
            if pkt.owner == 0:
                color = 'k'
            else:
                color = 'royalblue'
        rect = patches.Rectangle((start, freq), width, height,
                                 linewidth=1, linestyle='-', edgecolor=color, facecolor=color, fill=True,
                                 alpha=None, antialiased=False)
        ax.add_patch(rect)

# SF 12 lora packet
rect = patches.Rectangle((lora_pkt_start, 0), lora_pkt_t, grid.shape[0], label=r'LoRa device 3', linewidth=1, edgecolor='grey',
                         facecolor='darkgrey', fill=True, alpha=0.5)
ax.add_patch(rect)

ax.set_xlabel(r'Time (sec)', fontsize=16)
ax.set_ylabel(r'Channel frequency (MHz)', fontsize=16)
ax.set_xlim(0, 3800)
ax.set_ylim(0, grid.shape[0])
ax.set_yticks([0, grid.shape[0]/2, grid.shape[0]])
ax.set_yticklabels(['868.031', '868.1', '868.168'], fontsize=14)
ax.set_xticks(range(0, grid.shape[1], 1000))        # choose which x locations to have ticks
ax.set_xticklabels(range(0, 4, 1), fontsize=14)     # set the labels to display at those ticks
plt.text(318-170, 267-14, r'Header $1/3$', fontsize=11)
plt.text(551-170, 199-14, r'Header $2/3$', fontsize=11, color='red')
plt.text(784-170, 98-14, r'Header $3/3$', fontsize=11, color='red')
plt.text(2000, 185, r'Payload fragments', fontsize=11)
ax.plot(0, 0, c='k', label=r'LoRa--E device 1', linewidth=3.0, linestyle='-')
ax.plot(0, 0, c='royalblue', label=r'LoRa--E device 2 ~', linewidth=3.0, linestyle='-')
ax.plot(0, 0, c='red', label=r'Collided frames', linewidth=3.0, linestyle='-')
plt.legend(fontsize=12, loc='lower right')  # , ncol=3, loc='lower right')     # loc=(0.62, 0.78)
#fig.savefig('./images/grid.png', format='png', dpi=300)

plt.show(); plt.close()
