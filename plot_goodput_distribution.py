import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

lora_cr = 4/5
lora_e_cr = 1/3
percentage = 1.0
payload = 10 #bytes
gw_position = (689411, 689411, 0)

df = pd.read_csv('metrics.csv', index_col=0)

pkts_rx = df['pkt_sent'] - df['pkt_lost']
df.insert(3, 'pkt_rx', pkts_rx)

pkt_lost_ratio = df['pkt_lost'] / df['pkt_sent']
df.insert(4, 'pkt_lost_ratio', pkt_lost_ratio)

goodput = df['pkt_rx']*payload*lora_cr
df.insert(9, 'goodput', goodput)

total_goodput = df['goodput'].sum()

total_goodput_prop = df['goodput'] / total_goodput
df.insert(10, 'total_goodput_prop', total_goodput_prop)
df.insert(11, 'ones', np.ones(df.shape[0]))

fig, (ax1, ax2) = plt.subplots(1,2)

fig.suptitle("Considering RX Power")

#ax.hist(np.divide(lora_num_pkt_lost_list, lora_num_pkt_sent_list)*100, bins=max(lora_num_pkt_sent_list))
ax1.bar(range(0, df.shape[0]), np.divide(df['pkt_lost'], df['pkt_sent'])*100)
ax1.set_title("(lost_packets / sent_packets)*100 ratio per device")
ax1.set_xlabel("Device id")
ax1.set_ylabel("(lost_packets / sent_packets)*100 ratio")

hist_data = np.divide(df['pkt_lost'], df['pkt_sent'])*100
ax2.hist(hist_data+5, bins=np.linspace(0,100,11)+5, log=True, rwidth=0.8)
ax2.set_xticks(np.linspace(0,100,11))
ax2.set_title("Lost packets ratio per device distribution")
ax2.set_xlabel("Lost packets ratio")
ax2.set_ylabel("Num. devices")
ax2.set_xlim(-5, 105)

fig, ax3 = plt.subplots(1)

#df.plot(kind='bar', x='pkt_rx_power',y='goodput', ax=ax3)
bins_width = 6 #each bin is 6dBs wide
bins_left_bounds = list(range(-138, -15-bins_width, bins_width))
bins_rigth_bounds = list(range(-138+bins_width, -15, bins_width))
bins = pd.IntervalIndex.from_arrays(bins_left_bounds, bins_rigth_bounds)

rx_power_intervals = pd.cut(df['pkt_rx_power'], bins=bins)
df.insert(12, 'rx_power_interval', rx_power_intervals)
rx_power_intervals_value_counts = rx_power_intervals.value_counts()
#print(rx_power_intervals_value_counts)

df_grouped_rx_power_intervals = df.groupby('rx_power_interval').sum().sort_values('rx_power_interval',axis=0)

#df_grouped_rx_power_intervals_dict = df_grouped_rx_power_intervals.to_dict()
df_grouped_rx_power_intervals.rename(columns={'ones':'num_devices'}, inplace=True)
df_grouped_rx_power_intervals.insert(12, 'devices_proportion', df_grouped_rx_power_intervals['num_devices'] / df.shape[0])

#df['ones'] = [df_grouped_rx_power_intervals['ones'][interval] for interval in df['rx_power_interval']]
df_grouped_rx_power_intervals.reset_index(drop=False, inplace=True)
print(df_grouped_rx_power_intervals)
df_grouped_rx_power_intervals.plot(kind='bar', x='rx_power_interval', y='total_goodput_prop', position=0, color='blue', width=0.2, ax=ax3)
df_grouped_rx_power_intervals.plot(kind='bar', x='rx_power_interval', y='devices_proportion', mark_right=True, position=1, width=0.2, color='red', ax=ax3)

for i, v in enumerate(df_grouped_rx_power_intervals['devices_proportion']):
    ax3.text(i-0.3, v+0.01, str(int(round(df_grouped_rx_power_intervals['num_devices'][i],2))), color='k', fontweight='bold', fontsize=12)


fig, ax4 = plt.subplots(1)
df.plot(x='pos_x', y='pos_y', kind='scatter', color='blue', ax=ax4)
ax4.scatter(gw_position[0], gw_position[1], color='red')

plt.tight_layout()
plt.grid(True, alpha=0.5)
plt.show()
