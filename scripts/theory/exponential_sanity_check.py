from itertools import tee

import matplotlib.pyplot as plt
import numpy as np

import DeviceHelper
import TimeHelper


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


# SF12 10B
toa = 0.991  # seconds
t_off = 99.009

# ----------------------------------------
# Method 1
current_time = range(3600 * 100)

tx_time = []
this_time = 0
for i in range(len(current_time)):
    if current_time[i] >= this_time:
        # this_time = current_time[i] + random.expovariate(lambd=1. / (t_off + toa))
        this_time = TimeHelper.TimeHelper.next_time(current_time=current_time[i], step_time=(t_off + toa), mode='expo')
    tx_time.append(this_time)

# plt.plot(current_time, tx_time)
# plt.show()

dif = []
for v, w in pairwise(tx_time):
    if w - v != 0:
        dif.append(w - v)

plt.hist(dif, bins=100)
plt.title(f'Interval = {(t_off + toa)}, mean = {np.mean(dif)}')
plt.show()

# ----------------------------------------
# Method 2
tx_time = []
last_time_txed = 0
for i in range(len(current_time)):
    if current_time[i] >= last_time_txed + toa:
        last_time_txed = TimeHelper.TimeHelper.next_time(current_time=current_time[i], step_time=t_off, mode='expo')
    tx_time.append(last_time_txed)

# plt.plot(current_time, tx_time)
# plt.show()

dif = []
for v, w in pairwise(tx_time):
    if w - v != 0:
        dif.append(w - v)

plt.hist(dif, bins=100)
plt.title(f'Interval = {t_off}, mean = {np.mean(dif)}')
plt.show()


# -------------------
# EXAMPLE CASE : SF12 50B
toa, _, _ = DeviceHelper.DeviceHelper.get_time_on_air('notFHSS', None, pl_bytes=50, dr=3)
t_off = DeviceHelper.DeviceHelper.get_off_period(toa, dc=0.01)
toa = toa / 1000.
t_off = t_off / 1000.

t_interval = t_off + toa
lmbda = 1./t_interval

# ALOHA Throughput (the success rate!!!)
# max throughput is given when G = 0.5, G is lambda * N
# lambda is fixed when transmitting at max rate with DC constraint
# thus, num of devices needed to achieve max throughput is 0.5 / lambda = 50
N = 0.5 / lmbda
# check:
G = lmbda * N * toa
throughput = G * np.exp(-2 * G) # = 0.18393972058572117
# plot for n devices to see the maximum
throughput = []
G = []
for N in range(200):
    G = lmbda * N * toa
    throughput.append(G * np.exp(-2 * G))
plt.plot(throughput)
plt.show()

# NOW the PDR, i.e. P(success) given ALOHA when maximum throughput
G = 0.5     # lambda * 50 devices in this case
pdr = np.exp(-2 * G)    # = 0.36787944117144233
# pdr = []
# for N in range(400):
#     G = lmbda * N
#     pdr.append(np.exp(-2 * G))
# plt.plot(pdr)
# plt.show()