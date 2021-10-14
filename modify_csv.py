import numpy as np
import pandas as pd
import os

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


for results_dir in filter(lambda dir: os.path.isdir(dir) and dir.startswith('results_'), os.listdir()):
    _, annulus_width, type = results_dir.split('_')
    annulus_width = int(annulus_width.split('dB')[0])
    for lora_dr_dir in os.listdir(results_dir):
        #For each lora_dr
        lora_dr = int(lora_dr_dir.split('_')[1])
        for lora_e_dr_dir in os.listdir(f'{results_dir}/{lora_dr_dir}'):
            #For each lora_e_dr
            lora_e_dr = int(lora_e_dr_dir.split('_')[1])
            x = []
            y = []
            eff_br_ratio_std_pos = []
            eff_br_ratio_std_neg = []
            eff_br_std_pos = []
            eff_br_std_neg = []
            for payload_dir in os.listdir(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}'): 
                payload = int(payload_dir.split('_')[1])
                #for each payload_size
                for lora_devices_dir in filter(lambda x: x.startswith('CSS'), os.listdir(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}')):
                    lora_devices = int(lora_devices_dir.split('_')[1])
                    #for each num_lora_devices
                    for lora_e_devices_dir in sorted(os.listdir(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}'), key=lambda x: int(x.split('_')[1])):
                        #for each num_lora_e_devices
                        lora_e_devices = int(lora_e_devices_dir.split('_')[1])
                        lora_rx_pkts_per_run = []
                        lora_e_rx_pkts_per_run = []
                        lora_tx_pkts_per_run = []
                        lora_e_tx_pkts_per_run = []
                        num_runs = 0
                        for file in os.listdir(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}'):
                            # for each run   
                            data = pd.read_csv(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}/{file}')
                            data.insert(2, 'set', [1]*lora_devices + [2]*lora_e_devices)
                            data.to_csv(f'{results_dir}/{lora_dr_dir}/{lora_e_dr_dir}/{payload_dir}/{lora_devices_dir}/{lora_e_devices_dir}/{file}')
                            num_runs += 1
                        
