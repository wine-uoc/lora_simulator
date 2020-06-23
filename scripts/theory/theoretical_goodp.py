import matplotlib.pyplot as plt
import numpy as np

import LoraHelper


def get_lambda(mod, dr_bps, pl_size, dr):
    toa, _, _ = LoraHelper.LoraHelper.get_time_on_air(modulation=mod, dr_bps=dr_bps, pl_bytes=pl_size, dr=dr)
    t_off = LoraHelper.LoraHelper.get_off_period(toa, dc=dc)
    # to seconds
    toa = toa / 1000.
    t_off = t_off / 1000.
    t_interval = t_off + toa
    lmbda = 1. / t_interval
    return lmbda, toa


# -------------------

pl_size = 10
dc = 0.01

dr_a = [0, 1, 2, 3, 4, 5, 8, 9]
N = np.arange(10000)  # num of devices

#
p_suc = []
lmbd = []
good_p = []
for dr in dr_a:
    if dr == 8:
        bps = 162
        channels = 288
        cr = 1/3
    if dr == 9:
        bps = 325
        channels = 288
        cr = 2/3
    if dr < 8:
        bps = None
        mod = 'notFHSS'
        cr = 4/5
    else:
        mod = 'FHSS'
    lmbd_a, toa_a = get_lambda(mod, bps, pl_size, dr)
    lmbd.append(lmbd_a)

    # varying values
    G_a = lmbd_a * N * toa_a  # the offered load (if normalized toa_a should be = 1)

    # P(success)
    if dr < 8:
        p_suc_a = np.exp(-2 * G_a)
    else:
        # NOT ok:
        n_pl = toa_a / 0.050
        n_pl_coll = (1 - cr) * n_pl
        p_b_f = 1 - ((channels - 1) / channels) ** N  # coll on freq
        p_b_t = (1 - np.exp(-2 * 0.50 * lmbd_a * N)) ** n_pl_coll  # coll in time of payloads
        p_suc_a = 1 - (p_b_t * p_b_f)   # success

    p_suc.append(p_suc_a)  # success

    good_p.append(N * 3600./(1./lmbd_a) * pl_size * cr * p_suc_a)

# PDR is the same for each DR
for p in p_suc:
    plt.plot(N, p)
plt.grid()
plt.xscale('log')
plt.show()

# PDR is the same for each DR
plt.figure()
for i in range(len(good_p)):
    gp = good_p[i]
    #if dr_a[i] < 8:
    plt.plot(N, gp)
plt.grid(linestyle='-.', which='both')
#plt.ylim(10, 1000000)
plt.xlim(1, 500)
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel('Devices')
plt.ylabel('Goodput (bytes/hour)')
plt.title(f'PL size = {pl_size} bytes, DC = {dc}')
plt.show()
