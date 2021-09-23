import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import configparser

config = configparser.ConfigParser()
config.read('Simulator.cfg')

root_dir_name = config['simulator']['root_dir_name']

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

def compute_goodput(lora_rx_pkts, lora_e_rx_pkts, lora_e_dr, lora_dr, payload):
    return payload*(lora_rx_pkts*coding_rate[lora_dr] + lora_e_rx_pkts*coding_rate[lora_e_dr])

num_axes = len(os.listdir(root_dir_name))
height = int(np.round(np.sqrt(num_axes)))
width = int(np.floor(np.sqrt(num_axes)))+1
fig, axes = plt.subplots(height, width)
ax_i_idx = ax_j_idx = 0

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
                for lora_e_devices_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}'):
                    #for each num_lora_e_devices
                    lora_e_devices = int(lora_e_devices_dir.split('_')[1])
                    goodput_per_run = []
                    num_runs = 0
                    for file in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}'):
                        #for each run
                        # Get simulation info from file name     
                        data = pd.read_csv(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}/{file}')
                        pkt_rx = data['pkt_sent']-data['pkt_lost']
                        lora_rx_pkts = (pkt_rx.loc[data['modulation'] == 'CSS']).sum()
                        lora_e_rx_pkts = (pkt_rx.loc[data['modulation'] == 'FHSS']).sum()
                        goodput_per_run.append(compute_goodput(lora_rx_pkts, lora_e_rx_pkts, lora_e_dr, lora_dr, payload))
                        num_runs += 1
                    if num_runs != 0:
                        x.append(lora_e_devices)
                        y.append(np.array(goodput_per_run).mean())
                        gp_std_pos.append(np.array(goodput_per_run).mean() + np.array(goodput_per_run).std())
                        gp_std_neg.append(np.array(goodput_per_run).mean() - np.array(goodput_per_run).std())
    
    if height > 1:
        axes[ax_i_idx, ax_j_idx].plot(x,y)
        axes[ax_i_idx, ax_j_idx].set_title(f'DR{lora_dr}')
        axes[ax_i_idx, ax_j_idx].fill_between(x, gp_std_pos, gp_std_neg, alpha=0.2, color='r')
        axes[ax_i_idx, ax_j_idx].grid(True)
        axes[ax_i_idx, ax_j_idx].set_xscale('log')
        axes[ax_i_idx, ax_j_idx].set_yscale('log')
        if plot_num % (np.floor(np.sqrt(num_axes))+1) >= np.floor(np.sqrt(num_axes)):
            ax_i_idx += 1
            ax_j_idx = 0
        else:
            ax_j_idx += 1 
    else:
        axes[ax_j_idx].plot(x,y)
        axes[ax_j_idx].set_title(f'DR{lora_dr}')
        axes[ax_j_idx].fill_between(x, gp_std_pos, gp_std_neg, alpha=0.2, color='r')
        axes[ax_j_idx].grid(True)
        axes[ax_j_idx].set_xscale('log')
        axes[ax_j_idx].set_yscale('log')
        ax_j_idx += 1

    plot_num += 1
       
plt.tight_layout()
plt.grid(True)
plt.savefig('images/fhss_impact_on_css.png', dpi='figure')
plt.show()