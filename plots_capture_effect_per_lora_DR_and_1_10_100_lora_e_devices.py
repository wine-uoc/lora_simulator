import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_rows', 500)

coding_rate = {0: 4/5,
                1: 4/5,
                2: 4/5,
                3: 4/5,
                4: 4/5,
                5: 4/5,
                8: 1/3,
                9: 2/3,
                10: 1/3,
                11: 2/3}

bitrate = {0: 250, 1: 440, 2: 980 ,3: 1760, 4: 3125 , 5: 5470} #bits/s

df = pd.read_csv('simulation_data.csv', index_col=False)
df['lora_eff_bitrate'] = (df['payload_size']*df['lora_rx_pkts_mean']*df['lora_cr'])*8/3600
df.head()

df_1_10_100 = df[(df['type'] == 'POWER') & 
                    ((df['lora_e_devices'] == 1) | 
                    (df['lora_e_devices'] == 10) | 
                    (df['lora_e_devices'] == 100))].sort_values(by='annulus_width')

for lora_dr in df['lora_dr'].unique():
    fig, ax = plt.subplots()
    ax.set_title(f'Capture effect on LoRa DR{lora_dr} devices')
    ax.set_xticks(df_1_10_100['annulus_width'].unique())
    ax.grid(True, 'both')
    for lora_e_devices in df_1_10_100['lora_e_devices'].unique():
        df_1_10_100 = df_1_10_100[(df_1_10_100['lora_dr'] == lora_dr) &
                                    (df_1_10_100['lora_e_devices'] == lora_e_devices)]
        df_1_10_100_lora_e_dr_8 = df_1_10_100[(df_1_10_100['lora_e_dr'] == 8)]
        df_1_10_100_lora_e_dr_9 = df_1_10_100[(df_1_10_100['lora_e_dr'] == 9)]                       
        ax.plot(df_1_10_100['annulus_width'].unique(), df_1_10_100_lora_e_dr_8['lora_eff_bitrate'].to_numpy() / df_1_10_100_lora_e_dr_9['lora_eff_bitrate'].to_numpy(),
                marker='.')
plt.show() 