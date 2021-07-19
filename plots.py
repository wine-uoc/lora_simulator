import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
'''
Plots Goodput (bytes/hour) depending on the number of devices for each modulation (LoRa / LR-FHSS).
DR are fixed.
'''

df = pd.read_csv('results/results.csv', index_col=0)

# mean values of metrics for multiple runs
df_grouped = df.groupby(['N_devices', 'percentage', 'LoRa_DR', 'LR-FHSS_DR', 'payload'], as_index=False).agg({'LoRa_RX_pkts': np.mean, 'LR-FHSS_RX_pkts': np.mean})

# Add coding rate information
df_grouped['LoRa_CR'] = 4/5 # real data / total data
df_grouped['LR-FHSS_CR'] = df_grouped['LR-FHSS_DR'].apply(lambda dr: 1/3 if dr==8 or dr==10 else 2/3)

df_grouped.replace(to_replace=np.nan, value=0.0, inplace=True)

#Add goodput columns
df_grouped['Goodput'] = df_grouped['N_devices']*df_grouped['payload']*(df_grouped['percentage']*df_grouped['LoRa_RX_pkts']*df_grouped['LoRa_CR']+
                                                                        (1-df_grouped['percentage'])*df_grouped['LR-FHSS_RX_pkts']*df_grouped['LR-FHSS_CR'])

print(df_grouped)
fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')


#Scatter plot 3D


plot = ax.scatter(xs=df_grouped['N_devices'], ys=df_grouped['percentage'], zs=df_grouped['Goodput'], s=50.0, linewidth=3.0, linestyle='None', c=df_grouped['Goodput'], cmap='cividis')
ax.set_xlabel('Num. devices', fontsize=14)
ax.set_ylabel('LoRa ratio', fontsize=14)
ax.set_zlabel('Goodput', fontsize=14)
fig.colorbar(plot, ax=ax)


#Surface plot
'''
devs, perc = np.meshgrid(df_grouped['N_devices'].unique(), df_grouped['percentage'].unique())
gp = np.zeros(shape=(len(df_grouped['N_devices'].unique()), len(df_grouped['percentage'].unique())))
for i, d in enumerate(df_grouped['N_devices'].unique()):
    for j, p in enumerate(df_grouped['percentage'].unique()):
        gp[i,j] = df_grouped['Goodput'].loc[(df_grouped['N_devices'] == d) & (df_grouped['percentage'] == p)]
gp = gp.T
print(gp)
plot = ax.plot_surface(perc, devs, gp, cmap='viridis', linewidth=0, antialiased=False)
ax.set_xlabel('Num. devices', fontsize=14)
ax.set_ylabel('LoRa ratio', fontsize=14)
ax.set_zlabel('Goodput', fontsize=14)
fig.colorbar(plot, ax=ax)

'''
plt.show()