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

df = pd.DataFrame(columns=['type', 'annulus_width', 'devices_set_1', 'devices_set_2', 'dr_set_1', 'dr_set_2',
                            'mod_set_1', 'mod_set_2', 'cr_set_1', 'cr_set_2',
                            'tx_pkts_mean_set_1', 'tx_pkts_std_set_1', 'tx_pkts_mean_set_2', 'tx_pkts_std_set_2',
                            'rx_pkts_mean_set_1', 'rx_pkts_std_set_1', 'rx_pkts_mean_set_2', 'rx_pkts_std_set_2',
                            'payload_size'])

for results_dir in filter(lambda dir: os.path.isdir(dir) and dir.startswith('results_'), os.listdir()):
    _, annulus_width, type = results_dir.split('_')
    annulus_width = int(annulus_width.split('dB')[0])
    for set_1_dr_dir in os.listdir(results_dir):
        #For each lora_dr
        set_1_dr = int(set_1_dr_dir.split('_')[1])
        for set_2_dr_dir in os.listdir(f'{results_dir}/{set_1_dr_dir}'):
            #For each set_2_dr
            set_2_dr = int(set_2_dr_dir.split('_')[1])
            x = []
            y = []
            eff_br_ratio_std_pos = []
            eff_br_ratio_std_neg = []
            eff_br_std_pos = []
            eff_br_std_neg = []
            for payload_dir in os.listdir(f'{results_dir}/{set_1_dr_dir}/{set_2_dr_dir}'): 
                payload = int(payload_dir.split('_')[1])
                #for each payload_size
                for set_1_devices_dir in filter(lambda x: x.startswith('CSS') or x.startswith('FHSS'), os.listdir(f'{results_dir}/{set_1_dr_dir}/{set_2_dr_dir}/{payload_dir}')):
                    set_1_mod = set_1_devices_dir.split('_')[0]
                    set_1_devices = int(set_1_devices_dir.split('_')[1])
                    #for each num_set_1_devices
                    for set_2_devices_dir in sorted(os.listdir(f'{results_dir}/{set_1_dr_dir}/{set_2_dr_dir}/{payload_dir}/{set_1_devices_dir}'), key=lambda x: int(x.split('_')[1])):
                        #for each num_set_2_devices
                        set_2_mod = set_2_devices_dir.split('_')[0]
                        set_2_devices = int(set_2_devices_dir.split('_')[1])
                        rx_pkts_per_run_set_1 = []
                        rx_pkts_per_run_set_2 = []
                        tx_pkts_per_run_set_1 = []
                        tx_pkts_per_run_set_2 = []
                        num_runs = 0
                        for file in os.listdir(f'{results_dir}/{set_1_dr_dir}/{set_2_dr_dir}/{payload_dir}/{set_1_devices_dir}/{set_2_devices_dir}'):
                            # for each run   
                            data = pd.read_csv(f'{results_dir}/{set_1_dr_dir}/{set_2_dr_dir}/{payload_dir}/{set_1_devices_dir}/{set_2_devices_dir}/{file}')
                            rx_pkts = data['pkt_sent']-data['pkt_lost']
                            rx_pkts_set_1 = (rx_pkts.loc[data['set'] == 1]).sum()
                            rx_pkts_set_2 = (rx_pkts.loc[data['set'] == 2]).sum()
                            tx_pkts_set_1 = (data['pkt_sent'].loc[data['set'] == 1]).sum()
                            tx_pkts_set_2 = (data['pkt_sent'].loc[data['set'] == 2]).sum()
                            rx_pkts_per_run_set_1.append(rx_pkts_set_1)
                            rx_pkts_per_run_set_2.append(rx_pkts_set_2)
                            tx_pkts_per_run_set_1.append(tx_pkts_set_1)
                            tx_pkts_per_run_set_2.append(tx_pkts_set_2)
                            num_runs += 1
                        if num_runs != 0:
                            tx_pkts_mean_set_1 = np.array(tx_pkts_per_run_set_1).mean()
                            tx_pkts_std_set_1 = np.array(tx_pkts_per_run_set_1).std()
                            tx_pkts_mean_set_2 = np.array(tx_pkts_per_run_set_2).mean()
                            tx_pkts_std_set_2 = np.array(tx_pkts_per_run_set_2).std()
                            rx_pkts_mean_set_1 = np.array(rx_pkts_per_run_set_1).mean()
                            rx_pkts_std_set_1 = np.array(rx_pkts_per_run_set_1).std()
                            rx_pkts_mean_set_2 = np.array(rx_pkts_per_run_set_2).mean()
                            rx_pkts_std_set_2 = np.array(rx_pkts_per_run_set_2).std()
                            df = df.append(other={'type': type, 'annulus_width':annulus_width, 'devices_set_1':set_1_devices, 'devices_set_2':set_2_devices, 
                                            'dr_set_1': set_1_dr, 'dr_set_2': set_2_dr, 'mod_set_1':set_1_mod, 'mod_set_2':set_2_mod, 
                                            'cr_set_1': coding_rate[set_1_dr], 'cr_set_2': coding_rate[set_2_dr], 'tx_pkts_mean_set_1': tx_pkts_mean_set_1, 'tx_pkts_std_set_1': tx_pkts_std_set_1,
                                            'tx_pkts_mean_set_2': tx_pkts_mean_set_2, 'tx_pkts_std_set_2': tx_pkts_std_set_2, 'rx_pkts_mean_set_1': rx_pkts_mean_set_1,
                                            'rx_pkts_std_set_1': rx_pkts_std_set_1, 'rx_pkts_mean_set_2': rx_pkts_mean_set_2, 'rx_pkts_std_set_2': rx_pkts_std_set_2,
                                            'payload_size': payload}, ignore_index=True)

df.to_csv('simulation_data.csv')