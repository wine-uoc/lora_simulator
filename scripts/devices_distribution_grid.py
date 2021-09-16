import matplotlib.pyplot as plt
import numpy as np

num_devices_list = list(range(0,100000,10))

bins_width = 6 #each bin is 6dBs wide
rssi_values = list(range(-18, -137, -bins_width)) + [-137]
dist_values = list(map(lambda x: 10**((14-x-(20*np.log10(0.868))-92.45)/20.0), rssi_values))
furthest_dist = dist_values[-1]
annuluses_area = [np.pi*(val_act**2 - val_ant**2) for (val_act, val_ant) in list(zip(dist_values[1:], dist_values))]

num_devs_in_clusters_smaller_than_500_devs = []
for n_devs in num_devices_list:
    devs_density = n_devs/(np.pi * (furthest_dist**2))
    num_devs_in_each_annulus = list(map(lambda an_area: an_area*devs_density, annuluses_area))
    num_devs_in_clusters_smaller_than_500_devs.append(np.sum(num_devs_in_each_annulus, where=np.array(num_devs_in_each_annulus) <= 500))
    
plt.plot(num_devices_list, num_devs_in_clusters_smaller_than_500_devs)
plt.grid(True)
plt.show()



