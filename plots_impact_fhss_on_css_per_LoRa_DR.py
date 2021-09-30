import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import yaml

config = yaml.load(open('Simulator.yaml'), Loader=yaml.Loader)

root_dir_name = config['common']['root_dir_name']

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

lora_e_color = {8: 'r', 9:'b'}

def compute_LoRa_goodput(lora_rx_pkts, lora_dr, payload):
    return payload*(lora_rx_pkts*coding_rate[lora_dr])   # + lora_e_rx_pkts*coding_rate[lora_e_dr])

num_axes = len(os.listdir(root_dir_name))
height = int(np.round(np.sqrt(num_axes)))
width = int(np.floor(np.sqrt(num_axes)))+1
fig, axes = plt.subplots(height, width)
ax_i_idx = ax_j_idx = 0
fig.suptitle('FHSS impact on CSS', fontsize=16)
plot_num = 0
for lora_dr_dir in os.listdir(root_dir_name):
    #For each lora_dr
    lora_dr = int(lora_dr_dir.split('_')[1])
    for lora_e_dr_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}'):
        #For each lora_e_dr
        lora_e_dr = int(lora_e_dr_dir.split('_')[1])
        x = []
        y = []
        gp_std_pos = []
        gp_std_neg = []
        for payload_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}'): 
            payload = int(payload_dir.split('_')[1])
            #for each payload_size
            for lora_devices_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}'):
                lora_devices = int(lora_devices_dir.split('_')[1])
                #for each num_lora_devices
                for lora_e_devices_dir in sorted(os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}'), key=lambda x: int(x.split('_')[1])):
                    #for each num_lora_e_devices
                    lora_e_devices = int(lora_e_devices_dir.split('_')[1])
                    eff_bitrate_ratio_per_run = []
                    num_runs = 0
                    for file in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}'):
                        #for each run
                        # Get simulation info from file name     
                        data = pd.read_csv(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}/{file}')
                        pkt_rx = data['pkt_sent']-data['pkt_lost']
                        lora_rx_pkts = (pkt_rx.loc[data['modulation'] == 'CSS']).sum()
                        lora_e_rx_pkts = (pkt_rx.loc[data['modulation'] == 'FHSS']).sum()
                        eff_bitrate_ratio_per_run.append((compute_LoRa_goodput(lora_rx_pkts, lora_dr, payload)*8)/(3600*bitrate[lora_dr]))
                        num_runs += 1
                    if num_runs != 0:
                        x.append(lora_e_devices)
                        y.append(np.array(eff_bitrate_ratio_per_run).mean())
                        gp_std_pos.append(np.array(eff_bitrate_ratio_per_run).mean() + np.array(eff_bitrate_ratio_per_run).std())
                        gp_std_neg.append(np.array(eff_bitrate_ratio_per_run).mean() - np.array(eff_bitrate_ratio_per_run).std())
    
        if height > 1:
            axes[ax_i_idx, ax_j_idx].plot(x,y, label=f'DR{lora_e_dr}', c=lora_e_color[lora_e_dr], marker='.', markersize=9)
            axes[ax_i_idx, ax_j_idx].set_title(f'DR{lora_dr}')
            axes[ax_i_idx, ax_j_idx].set_xlabel('Num. LoRa-E devices')
            axes[ax_i_idx, ax_j_idx].set_ylabel('Effective bitrate ratio (ef. bitrate / max. bitrate)')
            axes[ax_i_idx, ax_j_idx].fill_between(x, gp_std_pos, gp_std_neg, alpha=0.2, color=lora_e_color[lora_e_dr])
            axes[ax_i_idx, ax_j_idx].grid(True, which='both', alpha=0.5)
            axes[ax_i_idx, ax_j_idx].set_xscale('log')
            #axes[ax_i_idx, ax_j_idx].set_yscale('log')
            axes[ax_i_idx, ax_j_idx].legend()
        else:
            axes[ax_j_idx].plot(x,y,label=f'DR{lora_e_dr}', c=lora_e_color[lora_e_dr], marker='.', markersize=9)
            axes[ax_j_idx].set_title(f'DR{lora_dr}')
            axes[ax_j_idx].set_xlabel('Num. LoRa-E devices')
            axes[ax_j_idx].set_ylabel('Effective bitrate ratio (ef. bitrate / max. bitrate)')
            axes[ax_j_idx].fill_between(x, gp_std_pos, gp_std_neg, alpha=0.2, color=lora_e_color[lora_e_dr])
            axes[ax_j_idx].grid(True, which='both', alpha=0.5)
            axes[ax_j_idx].set_xscale('log')
            #axes[ax_j_idx].set_yscale('log')
            axes[ax_j_idx].legend()
            #ax_j_idx += 1

    if height > 1:
        if plot_num % (np.floor(np.sqrt(num_axes))+1) >= np.floor(np.sqrt(num_axes)):
                ax_i_idx += 1
                ax_j_idx = 0
        else:
            ax_j_idx += 1
    else:
        ax_j_idx += 1

    plot_num += 1
       
plt.tight_layout()
plt.savefig('images/effective_bitrate_ratio_per_CSS_DR_6dB.png', dpi='figure')
plt.show()