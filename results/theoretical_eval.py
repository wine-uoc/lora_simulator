import matplotlib.pyplot as plt
import numpy as np

import DeviceHelper

# -------------------
# A: lora case
# B: LoRa case
dr_a = 0
dr_b = 8
pl_size = 10
dc = 0.01
channels = 288


# fixed values
def get_lambda(mod, dr_bps, pl_size, dr):
    toa, _, _ = DeviceHelper.DeviceHelper.get_time_on_air(modulation=mod, dr_bps=dr_bps, pl_bytes=pl_size, dr=dr)
    t_off = DeviceHelper.DeviceHelper.get_off_period(toa, dc=dc)
    # to seconds
    toa = toa / 1000.
    t_off = t_off / 1000.
    t_interval = t_off + toa
    lmbda = 1./t_interval
    return lmbda, toa


# rate per node
lmbd_a, toa_a = get_lambda('notFHSS', None, pl_size, dr_a)
lmbd_b, toa_b = get_lambda('FHSS', 162, pl_size, dr_b)

# varying values
N = np.arange(10000)     # num of devices
G_a = lmbd_a * N * toa_a     # the offered load
G_b = lmbd_b * N * toa_b     # the offered load

# P(success)
p_a = np.exp(-2 * G_a)  # success
p_b_f = 1 - ((channels - 1) / channels) ** N    # coll on freq
p_b_t = (1 - np.exp(-2 * 0.50 * lmbd_b * N)) ** 3      # TODO: coll in time (like un-slotted aloha with slots of 50ms and 1/3 (CR))
p_b = 1 - (p_b_t * p_b_f)     # success

plt.plot(N, p_a, label='pa')
plt.plot(N, p_b_f, label='pbf')
plt.plot(N, p_b_t, label='pbt')
plt.plot(N, p_b, label='pab')
plt.legend()
plt.xscale('log')
plt.grid()
plt.show()

# Throughput (the success rate!!!): offered load * P(success)
throughput_a = G_a * p_a
throughput_b = G_b * p_b

plt.plot(N, throughput_a, label='a')
plt.plot(N, throughput_b, label='b')
#plt.yscale('log')
plt.xscale('log')
plt.legend()
plt.grid()
plt.show()



