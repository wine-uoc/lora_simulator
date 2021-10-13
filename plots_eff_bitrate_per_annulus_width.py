import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('simulation_data.csv', index_col=False)
df['lora_eff_bitrate'] = (df['payload_size']*df['lora_rx_pkts_mean']*df['lora_cr'])*8/3600

fig, ax = plt.subplots(figsize=(15,15))

df_dr5_dr8_1_10_100 = df[(df['lora_dr'] == 5) & 
                        (df['lora_e_dr'] == 8) &
                        ((df['lora_e_devices'] == 1) |
                        (df['lora_e_devices'] == 10) |
                        (df['lora_e_devices'] == 100))].sort_values(by='annulus_width', axis=0)

print(df_dr5_dr8_1_10_100)

for lora_e_devices in df_dr5_dr8_1_10_100['lora_e_devices'].unique():
    #for type in df_dr5_dr8_1_10_100['type'].unique():
    data_to_plot_POWER = df_dr5_dr8_1_10_100[(df_dr5_dr8_1_10_100['type'] == 'POWER') & (df_dr5_dr8_1_10_100['lora_e_devices'] == lora_e_devices)]
    data_to_plot_DISTANCE = df_dr5_dr8_1_10_100[(df_dr5_dr8_1_10_100['type'] == 'DISTANCE') & (df_dr5_dr8_1_10_100['lora_e_devices'] == lora_e_devices)]
    ax.plot(data_to_plot_POWER['annulus_width'], data_to_plot_POWER['lora_eff_bitrate'].to_numpy()/data_to_plot_DISTANCE['lora_eff_bitrate'].to_numpy(), 
        label=f'lora_e_devices={lora_e_devices}', 
        marker='.', markersize=12)
    lora_eff_bitrate_gain_pos = ((data_to_plot_POWER['payload_size']*(data_to_plot_POWER['lora_rx_pkts_mean'] + data_to_plot_POWER['lora_rx_pkts_std'])*data_to_plot_POWER['lora_cr'])*8/3600).to_numpy()/ \
                           ((data_to_plot_DISTANCE['payload_size']*(data_to_plot_DISTANCE['lora_rx_pkts_mean'] + data_to_plot_DISTANCE['lora_rx_pkts_std'])*data_to_plot_DISTANCE['lora_cr'])*8/3600).to_numpy()
    lora_eff_bitrate_gain_neg = ((data_to_plot_POWER['payload_size']*(data_to_plot_POWER['lora_rx_pkts_mean'] - data_to_plot_POWER['lora_rx_pkts_std'])*data_to_plot_POWER['lora_cr'])*8/3600).to_numpy()/ \
                           ((data_to_plot_DISTANCE['payload_size']*(data_to_plot_DISTANCE['lora_rx_pkts_mean'] - data_to_plot_DISTANCE['lora_rx_pkts_std'])*data_to_plot_DISTANCE['lora_cr'])*8/3600).to_numpy()
    ax.fill_between(data_to_plot_POWER['annulus_width'], lora_eff_bitrate_gain_pos, lora_eff_bitrate_gain_neg, alpha=0.2)

ax.set_xlabel('annulus width (dB)')
ax.set_ylabel('LoRa eff. bitrate gain')
ax.set_title('DR5-DR8 LoRa eff. bitrate gain (POWER / DISTANCE)')
ax.set_xticks(df['annulus_width'].unique())
ax.legend(loc='center right', fontsize=10)
ax.grid(True)
plt.show()

