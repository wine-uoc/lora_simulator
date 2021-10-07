import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

def loguniform(low=0, high=1, size=None, base=np.e):
    return np.power(base, np.random.uniform(low, high, size))

fspl = lambda d : 20*np.log10(d/1000.0) + 20*np.log10(868.0/1000.0) + 92.45
dist = np.power(10, np.random.uniform(155,600,300))
power_loss = fspl(dist)

fig = plt.figure()
gs = GridSpec(4, 4)

ax_scatter = fig.add_subplot(gs[1:4, 0:3])
ax_scatter.set_xlabel("Distance (m)")
ax_scatter.set_ylabel("dB")

ax_hist_x = fig.add_subplot(gs[0,0:3])
ax_hist_x.set_ylabel("Frequency")

ax_hist_y = fig.add_subplot(gs[1:4, 3])
ax_hist_y.set_xlabel("Frequency")

ax_scatter.scatter(dist, power_loss)
ax_hist_x.hist(dist)
ax_hist_y.hist(power_loss, orientation = 'horizontal')

plt.show()