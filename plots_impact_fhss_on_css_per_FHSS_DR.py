import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import configparser

config = configparser.ConfigParser()
config.read('Simulator.cfg')

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
lora_color = {0: 'b', 1: 'g', 2:'r', 3:'c', 4:'m', 5:'y'}

def compute_LoRa_goodput(lora_rx_pkts, lora_dr, payload):
    return payload*(lora_rx_pkts*coding_rate[lora_dr])   # + lora_e_rx_pkts*coding_rate[lora_e_dr])

num_axes = len(os.listdir(root_dir_name))
height = int(np.round(np.sqrt(num_axes)))
width = int(np.floor(np.sqrt(num_axes)))+1


fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()

for lora_dr_dir in os.listdir(root_dir_name):
    #For each lora_dr
    lora_dr = int(lora_dr_dir.split('_')[1])
    for lora_e_dr_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}'):
        #For each lora_e_dr
        lora_e_dr = int(lora_e_dr_dir.split('_')[1])
        x = []
        y = []
        eff_br_ratio_std_pos = []
        eff_br_ratio_std_neg = []
        eff_br_std_pos = []
        eff_br_std_neg = []
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
                    eff_bitrate_per_run = []
                    num_runs = 0
                    for file in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}'):
                        # for each run
                        # Get simulation info from file name     
                        data = pd.read_csv(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}/{file}')
                        pkt_rx = data['pkt_sent']-data['pkt_lost']
                        lora_rx_pkts = (pkt_rx.loc[data['modulation'] == 'CSS']).sum()
                        lora_e_rx_pkts = (pkt_rx.loc[data['modulation'] == 'FHSS']).sum()
                        eff_bitrate_ratio_per_run.append((compute_LoRa_goodput(lora_rx_pkts, lora_dr, payload)*8)/(3600*bitrate[lora_dr]))
                        eff_bitrate_per_run.append((compute_LoRa_goodput(lora_rx_pkts, lora_dr, payload)*8)/3600)
                        num_runs += 1
                    if num_runs != 0:
                        x.append(lora_e_devices)
                        y.append(np.array(eff_bitrate_ratio_per_run).mean())
                        eff_br_ratio_std_pos.append(np.array(eff_bitrate_ratio_per_run).mean() + np.array(eff_bitrate_ratio_per_run).std())
                        eff_br_ratio_std_neg.append(np.array(eff_bitrate_ratio_per_run).mean() - np.array(eff_bitrate_ratio_per_run).std())
                        eff_br_std_pos.append(np.array(eff_bitrate_per_run).mean() + np.array(eff_bitrate_per_run).std())
                        eff_br_std_neg.append(np.array(eff_bitrate_per_run).mean() - np.array(eff_bitrate_per_run).std())

        if lora_e_dr == 8:
            ax1.plot(x,y, label=f'DR{lora_dr}', color=lora_color[lora_dr], marker='.', markersize=9)
            ax1.set_title(f'DR{lora_e_dr}')
            ax1.set_xlabel('Num. LoRa-E devices')
            ax1.set_ylabel('Effective bitrate ratio (ef. bitrate / max. bitrate)')
            ax1.fill_between(x, eff_br_ratio_std_pos, eff_br_ratio_std_neg, alpha=0.2, color=lora_color[lora_dr])
            ax1.grid(True, which='both', alpha=0.5)
            ax1.set_xscale('log')
            #axes[ax_j_idx].set_yscale('log')
            ax1.legend()

            ax3.plot(x,np.array(y)*bitrate[lora_dr], label=f'DR{lora_dr}', color=lora_color[lora_dr], marker='.', markersize=9)
            ax3.set_title(f'DR{lora_e_dr}')
            ax3.set_xlabel('Num. LoRa-E devices')
            ax3.set_ylabel('Effective bitrate (B/s)')
            ax3.fill_between(x, eff_br_std_pos, eff_br_std_neg, alpha=0.2, color=lora_color[lora_dr])
            ax3.grid(True, which='both', alpha=0.5)
            ax3.set_xscale('log')
            ax3.legend()
       
        elif lora_e_dr == 9:
            ax2.plot(x,y, label=f'DR{lora_dr}', color=lora_color[lora_dr], marker='.', markersize=9)
            ax2.set_title(f'DR{lora_e_dr}')
            ax2.set_xlabel('Num. LoRa-E devices')
            ax2.set_ylabel('Effective bitrate ratio (ef. bitrate / max. bitrate)')
            ax2.fill_between(x, eff_br_ratio_std_pos, eff_br_ratio_std_neg, alpha=0.2, color=lora_color[lora_dr])
            ax2.grid(True, which='both', alpha=0.5)
            ax2.set_xscale('log')
            #axes[ax_j_idx].set_yscale('log')
            ax2.legend()
            #ax_j_idx += 1

            ax4.plot(x,np.array(y)*bitrate[lora_dr], label=f'DR{lora_dr}', color=lora_color[lora_dr], marker='.', markersize=9)
            ax4.set_title(f'DR{lora_e_dr}')
            ax4.set_xlabel('Num. LoRa-E devices')
            ax4.set_ylabel('Effective bitrate (B/s)')
            ax4.fill_between(x, eff_br_std_pos, eff_br_std_neg, alpha=0.2, color=lora_color[lora_dr])
            ax4.grid(True, which='both', alpha=0.5)
            ax4.set_xscale('log')
            ax4.legend()

       
plt.tight_layout()
plt.savefig('images/eff_bitrate_abs_and_ratio_per_FHSS_DR_6dB.png', dpi='figure')
plt.show()