import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})

# load grid
grid = np.load('results/grid.npy', allow_pickle=True)

nr, nc = grid.shape

# integer matrix for colors
values = np.empty((2, 3), dtype=int)
owner_0_values = [1, 2, 3]  # col 0: header, col1: pl, col2: collision
owner_1_values = [4, 5, 6]
values[0] = owner_0_values
values[1] = owner_1_values

# transform grid to predefined colors
x_coll = []
y_coll = []
for row in range(nr):
    for col in range(nc):
        if grid[row, col] != 0 and grid[row, col] != -1:
            owner, number, part = grid[row, col].split('.')
            print(f'{owner}, {number}, {part}')
            this_part = int(part)
            this_owner = int(owner)
            if this_owner == 0:
                if 0 <= this_part <= 1:
                    # color = 0
                    pass
                elif 1 < this_part <= 16:
                    # color = 2
                    x_coll.append(col)
                    y_coll.append(row)
                else:
                    # color = 1
                    pass
            if this_owner == 1:
                if 0 <= this_part < 1:
                    # color = 0
                    pass
                elif 1 <= this_part <= 2:
                    # color = 2
                    x_coll.append(col)
                    y_coll.append(row)
                else:
                    # color = 1
                    pass
            # color header and pl only
            if this_part <= 2:
                color = 0
            else:
                color = 1
            grid[row, col] = values[this_owner, color]


# Latex
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# color association to integer matrix
# cmap = colors.ListedColormap(['white', 'goldenrod', 'darkgoldenrod', 'k', 'royalblue', 'navy', 'red'])
cmap = colors.ListedColormap(['white', 'k', 'k', 'royalblue', 'royalblue', 'royalblue', 'red'])
bounds = [0, 1, 2, 3, 4, 5, 6, 7]
norm = colors.BoundaryNorm(bounds, cmap.N)

# create figure
fig, ax = plt.subplots(1)

# image
img = ax.pcolormesh(grid.astype(int), cmap=cmap, norm=norm)  # origin="lower", aspect='auto', interpolation='nearest')

# sf12 packet
rect = patches.Rectangle((4000, 0), 991, 1000, label=r'LoRa DR0 (SF12)', linewidth=1, edgecolor='grey',
                         facecolor='grey', fill=True, alpha=0.5)
ax.add_patch(rect)
# rect = patches.Rectangle((3500, 200), 1000, 3, linewidth=0.5, edgecolor='red', facecolor=None, fill=False, label='Packet Collided')
# ax.add_patch(rect)

# coll circles
last_y_coll = -1
for i in range(len(x_coll)):
    if last_y_coll != y_coll[i]:
        if y_coll[i] == 206 or y_coll[i] == 239 or y_coll[i] == 124:
            offset = 360
        else:
            offset = 0
        ax.scatter(x_coll[i] + offset, y_coll[i], marker='o', s=150, c='r', alpha=0.5)
        last_y_coll = y_coll[i]

# dummy for labels
ax.plot(0, 0, c='k', label=r'LoRa--E DR8 device 1', linewidth=3.0, linestyle='-')
ax.plot(0, 0, c='royalblue', label=r'LoRa--E DR8 device 2', linewidth=3.0, linestyle='-')
ax.scatter(0, 0, marker='o', s=100, c='r', alpha=0.5, label=r'Frame collision')

ax.set_xlabel(r'Time (sec)', fontsize=16)
ax.set_ylabel(r'Physical  sub-carrier', fontsize=16)
ax.set_xlim(2000, 8000)
ax.set_ylim(100, 250)
ax.set_xticks(range(2000, 8001, 1000))  # choose which x locations to have ticks
ax.set_xticklabels(range(0, 8, 1), fontsize=14)  # set the labels to display at those ticks
plt.yticks(range(100, 300, 25), fontsize=14)
# plt.colorbar(img)
plt.text(2170, 225, r'Header $1/3$', fontsize=10)
plt.text(2870, 175, r'Header $2/3$', fontsize=10)
plt.text(3570, 212, r'Header $3/3$', fontsize=10)
plt.text(6500, 254, r'Payloads', fontsize=14)
plt.legend(fontsize=12, loc='lower right', framealpha=1)  # , ncol=3, loc='lower right')     # loc=(0.62, 0.78)
fig.savefig('./results/images/grid.png', format='png', dpi=200)
plt.show()
plt.close()

# suma = 0
# for i in range(len(x_coll)):
#     if y_coll[i] == 206:
#         if suma == 0:
#             print(i)
#         suma = suma +1
# header duration is 704