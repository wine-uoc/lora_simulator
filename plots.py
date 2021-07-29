from matplotlib.colors import Colormap
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

'''
Plots Goodput (bytes/hour) depending on the number of devices for each modulation (LoRa / LR-FHSS).
DR are fixed.
'''

df = pd.read_csv('results/results.csv', index_col=0)
PLOT_TYPE = 2

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

#Scatter plot 3D
if PLOT_TYPE == 0:
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    plot = ax.scatter(xs=df_grouped['N_devices'], ys=df_grouped['percentage'], zs=df_grouped['Goodput'], s=50.0, linewidth=3.0, linestyle='None', c=df_grouped['Goodput'], cmap='cividis')
    ax.set_xlabel('Num. devices', fontsize=14)
    ax.set_ylabel('LoRa ratio', fontsize=14)
    ax.set_zlabel('Goodput', fontsize=14)
    fig.colorbar(plot, ax=ax)
    plt.savefig("images/scatter.png", dpi=200)
    

#Surface plot
if PLOT_TYPE == 1:
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    devs, perc = np.meshgrid(df_grouped['N_devices'].unique(), df_grouped['percentage'].unique())
    gp = np.zeros(shape=(len(df_grouped['N_devices'].unique()), len(df_grouped['percentage'].unique())))
    for i, d in enumerate(df_grouped['N_devices'].unique()):
        for j, p in enumerate(df_grouped['percentage'].unique()):
            gp[i,j] = df_grouped['Goodput'].loc[(df_grouped['N_devices'] == d) & (df_grouped['percentage'] == p)]
    gp = gp.T
    plot = ax.plot_surface(devs, perc, np.log10(gp+1), cmap='viridis', linewidth=0, antialiased=False, alpha=0.5)
    ax.set_xlabel('Num. devices', fontsize=14)
    ax.set_ylabel('LoRa ratio', fontsize=14)
    ax.set_zlabel('Goodput', fontsize=14)
    fig.colorbar(plot, ax=ax)
    plt.savefig("images/surface.png", dpi=200)

# Line plot for each lora_ratio
if PLOT_TYPE == 2:
    fig = plt.figure()
    ax = fig.add_subplot(111)

    percentages = pd.unique(df_grouped['percentage'])
    devices = pd.unique(df_grouped['N_devices'])
    ax.set_xlabel('Num_devices', fontsize=14)
    ax.set_ylabel('Goodput (bytes/hour)', fontsize=14)
    for p in percentages:
        plt.plot(devices,df_grouped['Goodput'].loc[df_grouped['percentage'] == p]+1, label=f'LoRa_ratio = {p}', linewidth=2)
        plt.xscale('log')
        plt.yscale('log')
    plt.legend()
    plt.yticks()

'''
Plots number of LoRa-E packets collided with a LoRa packet through an histogram
'''

fig = plt.figure()
ax2 = fig.add_subplot(111)
ax2.set_xlabel('Num. collisions', fontsize=14)
ax2.set_ylabel('Frames ratio', fontsize=14)

data = pd.read_csv('lora_packets_collisions.csv', header=None, index_col=0)
labels, counts = np.unique(data, return_counts=True)
#Remove non collided frames
labels = labels[1:]
counts = counts[1:]
plt.bar(labels, list(map(lambda x: x/np.sum(counts), counts)), align='center')
plt.gca().set_xticks(labels)

plt.show()
