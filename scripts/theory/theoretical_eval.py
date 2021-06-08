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
hop_duration_sec = 0.050


# fixed values
def get_lambda(mod, dr_bps, pl_size, dr):
    toa, t_h, t_pl = DeviceHelper.DeviceHelper.get_time_on_air(modulation=mod, dr_bps=dr_bps, pl_bytes=pl_size, dr=dr)
    t_off = DeviceHelper.DeviceHelper.get_off_period(toa, dc=dc)
    # to seconds
    toa = toa / 1000.
    t_off = t_off / 1000.
    t_interval = t_off + toa
    lmbda = 1. / t_interval
    return lmbda, toa, t_h / 1000., t_pl / 1000.


# rate per node
lmbd_a, toa_a, _, _ = get_lambda('notFHSS', None, pl_size, dr_a)  # lora SF12
lmbd_b, toa_b, t_h, t_pl = get_lambda('FHSS', 162, pl_size, dr_b)  # loraE DR8
header_reps = 3
cr = 1 / 3

# num of pl fragments collided to not decode a pkt
n_pl = t_pl / hop_duration_sec
n_pl_coll = (1 - cr) * n_pl

# varying values
N = np.arange(10000)  # num of devices
G_a = lmbd_a * N * toa_a  # the offered load (if normalization toa_a should be = 1)
G_b = lmbd_b * N * toa_b  # the offered load

# P(success) lora
p_a = np.exp(-2 * G_a)  # success

# P(success) loraE
# TODO: correct coll in time (like un-slotted aloha with slots of 50ms for pl and 1/3 CR plus headers ...)
p_b_t_pl = (1 - np.exp(-2 * 0.50 * lmbd_b * N)) ** n_pl_coll  # coll in time of 1-cr payloads
p_b_t_h = (1 - np.exp(-2 * t_h * lmbd_b * N)) ** header_reps  # coll in time of all headers
p_b_t = p_b_t_pl * p_b_t_h
p_b_f = 1 - ((channels - 1) / channels) ** N  # coll on freq
p_b = 1 - (p_b_t * p_b_f)  # success: 1 - coll_freq * coll_time

plt.plot(N, p_a, label='pa success')
plt.plot(N, p_b_f, label='pbf collision')
plt.plot(N, p_b_t, label='pbt collision')
plt.plot(N, p_b, label='pb success')
plt.legend()
plt.xscale('log')
plt.grid()
plt.show()

# Throughput (the success rate!!!): offered load * P(success)
throughput_a = G_a * p_a
throughput_b = G_b * p_b
plt.plot(N, throughput_a, label='a')
plt.plot(N, throughput_b, label='b')
plt.xscale('log')
plt.legend()
plt.grid()
plt.show()

# Goodput intersection Lora - LoraE
g_a = N * 3600. / (1. / lmbd_a) * pl_size * p_a
g_b = N * 3600. / (1. / lmbd_b) * pl_size * p_b
idx = np.argwhere(np.diff(np.sign(g_a - g_b))).flatten()
plt.plot(N[idx], g_a[idx], 'ro')
plt.plot(N, g_a, label='a')
plt.plot(N, g_b, label='b')
plt.legend()
plt.grid()
plt.yscale('log')
plt.xscale('log')
plt.xlim(1, 10000)
plt.ylim(10, 1000000)
plt.show()
