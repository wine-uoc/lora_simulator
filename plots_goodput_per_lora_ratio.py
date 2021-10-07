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

lora_e_color = {8: 'r', 9:'b'}
lora_ratio_color = {0: 'b', 1: 'g', 2:'r', 3:'c', 4:'m', 5:'y'}

def compute_LoRa_goodput(lora_rx_pkts, lora_dr, lora_e_rx_pkts, lora_e_dr, payload):
    return payload*(lora_rx_pkts*coding_rate[lora_dr] + lora_e_rx_pkts*coding_rate[lora_e_dr])

num_axes = len(os.listdir(root_dir_name))
height = int(np.round(np.sqrt(num_axes)))
width = int(np.floor(np.sqrt(num_axes)))+1




for lora_dr_dir in os.listdir(root_dir_name):
    #For each lora_dr
    lora_dr = int(lora_dr_dir.split('_')[1])
    for lora_e_dr_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}'):
        #For each lora_e_dr
        lora_e_dr = int(lora_e_dr_dir.split('_')[1])
        for payload_dir in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}'): 
            payload = int(payload_dir.split('_')[1])
            #for each payload_size
            fig, ax = plt.subplots()
            fig.suptitle('Total goodput for different ratios of LoRa devices')
            ax.set_title(f'LoRa DR = {lora_dr}, LR-FHSS DR = {lora_e_dr}, payload = {payload}B', color='gray', fontsize=10)
            ax.set_xlabel('Num. total devices')
            ax.set_ylabel('Total goodput (B/h)')
            for lora_ratio_dir in filter(lambda x: x.startswith('ratio'), os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}')):
                lora_ratio = float(lora_ratio_dir.split('_')[1])
                #for each num_lora_devices
                x = []
                y = []
                goodput_std_pos = []
                goodput_std_neg = []
                for num_devices_dir in sorted(os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_ratio_dir}'), key=lambda x: int(x.split('_')[0])):
                    #for each num_lora_e_devices
                    num_devices = int(num_devices_dir.split('_')[0])
                    goodput_per_run = []
                    num_runs = 0
                    for file in os.listdir(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_ratio_dir}/{num_devices_dir}'):
                        # for each run
                        # Get simulation info from file name     
                        data = pd.read_csv(f'{root_dir_name}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_ratio_dir}/{num_devices_dir}/{file}')
                        pkt_rx = data['pkt_sent']-data['pkt_lost']
                        lora_rx_pkts = (pkt_rx.loc[data['modulation'] == 'CSS']).sum()
                        lora_e_rx_pkts = (pkt_rx.loc[data['modulation'] == 'FHSS']).sum()
                        goodput_per_run.append((compute_LoRa_goodput(lora_rx_pkts, lora_dr, lora_e_rx_pkts, lora_e_dr, payload)))
                        num_runs += 1
                    if num_runs != 0:
                        x.append(num_devices)
                        y.append(np.array(goodput_per_run).mean())
                        goodput_std_pos.append(np.array(goodput_per_run).mean() + np.array(goodput_per_run).std())
                        goodput_std_neg.append(np.array(goodput_per_run).mean() - np.array(goodput_per_run).std())

                ax.plot(x,y, label=f'LoRa ratio={lora_ratio}', marker='.', markersize=9)

            ax.fill_between(x, goodput_std_pos, goodput_std_neg, alpha=0.2)
            ax.grid(True, which='both', alpha=0.5)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.legend()
        

       
plt.tight_layout()
#plt.savefig('images/eff_bitrate_abs_and_ratio_per_FHSS_DR_6dB.png', dpi='figure')
plt.show()