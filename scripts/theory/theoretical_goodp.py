import matplotlib.pyplot as plt
import numpy as np

import LoraHelper


def get_lambda(mod, dr_bps, pl_size, dr):
    """Returns the lambda and time on air."""
    toa, _, _ = LoraHelper.LoraHelper.get_time_on_air(
        modulation=mod, dr_bps=dr_bps, pl_bytes=pl_size, dr=dr
    )
    t_off = LoraHelper.LoraHelper.get_off_period(toa, dc=dc)
    # to seconds
    toa = toa / 1000.
    t_off = t_off / 1000.
    t_interval = t_off + toa
    lmbda = 1. / t_interval
    return lmbda, toa


# -------------------
# Sim parameters
pl_size = 10                        # payload size in bytes
dc = 0.01                           # duty cycle
dr_list = [0, 1, 2, 3, 4, 5, 8, 9]  # data rates
N = np.arange(1e5)                  # num of devices

# -------------------
# Caculate PDR and goodput for each parameter
p_suc = []
lmbd = []
good_p = []
for dr in dr_list:
    # hardcoded values for each dr
    if dr < 8:
        bps = None
        mod = "notFHSS"
        cr = 4 / 5
    else:
        mod = "FHSS"

    if dr == 8:
        bps = 162
        channels = 288
        cr = 1 / 3

    if dr == 9:
        bps = 325
        channels = 288
        cr = 2 / 3

    # Lambda and ToA
    lmbd_a, toa_a = get_lambda(mod, bps, pl_size, dr)
    lmbd.append(lmbd_a)

    # P(success)
    if dr < 8:
        # Pure ALOHA
        G_a = lmbd_a * N * toa_a  # the offered load (if normalized toa_a should be = 1)
        p_suc_a = np.exp(-2 * G_a)
    else:
        # FHSS with 0.050 sec hops
        # NOT OK, headers missing !!!
        n_pl = toa_a / 0.050            # num fragments
        n_pl_coll = (1 - cr) * n_pl     # num of lost fragments to consider a collision 
        
        # P_coll in freq domain:
        p_b_f = 1 - ((channels - 1) / channels) ** N  
        
        # P_coll in time: 
        p_b_t = (
            1 - np.exp(-2.0 * toa_a * lmbd_a * N)
        ) ** n_pl_coll  

        # P_sucess
        p_suc_a = 1 - (p_b_t * p_b_f)  

    # PDR, success
    p_suc.append(p_suc_a)

    # Goodput
    good_p.append(N * 3600. / (1. / lmbd_a) * pl_size * cr * p_suc_a)


# -------------------
# PLOTS
# PDR is the same for each DR
plt.figure()
for gp in good_p:
    plt.plot(N, gp)
plt.grid(linestyle="-.", which="both")
plt.ylim(10, 1e6)
plt.xlim(1, N[-1])
plt.yscale("log")
plt.xscale("log")
plt.xlabel("Devices")
plt.ylabel("Goodput (bytes/hour)")
plt.title(f"PL size = {pl_size} bytes, DC = {dc}")
plt.show()

# PDR is the same for each DR < 8
plt.figure()
for p in p_suc:
    plt.plot(N, p)
plt.grid()
plt.xlabel("Devices")
plt.ylabel("PDR")
plt.xscale("log")
plt.show()
plt.close()
