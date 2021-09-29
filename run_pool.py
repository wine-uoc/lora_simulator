"""
Received frames vs number of devices @ maximum transmission rate
"""
import os
from struct import Struct
import pandas as pd
from multiprocessing import Pool
import multiprocessing as mp
import numpy as np
import configparser

python = "python3"
script = "Simulator.py"
config_file = "Simulator.cfg"

config = configparser.ConfigParser()
config.read(config_file)

result_file = '{}/{}_{}_{}_{}_{}_{}_'
result_ext = ".npy"

area_side_size = int(config.get('common', 'area_side_size'))
time = int(config.get('common', 'time'))
step = int(config.get('common', 'step'))
interval = int(config.get('common', 'interval'))
position_mode = config.get('common', 'position_mode')
time_mode = config.get('common', 'time_mode')
payload_size = int(config.get('common', 'payload_size'))
dr_allocation_mode = config.get('common', 'DR_allocation_mode')
random = int(config.get('common', 'random'))
devices_tx_power = int(config.get('common', 'devices_tx_power'))
num_runs = int(config.get('common', 'num_runs'))
dr_auto_select = int(config.get('LoRa', 'LoRa_auto_DR_selection'))

def run_simulation(run, lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR):
    

    print('Running test with parameters lora_devices={}, lora_e_devices={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format(lora_devices,
                                                                                                                            lora_e_devices,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload_size,
                                                                                                                            run,
                                                                                                                            num_runs))
    log_file = result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'
    command = "{} {} -s {} -n {} -da {} -de {} -t {} -st {} -i {} -pm {} -tm {} -am {} -pl {} -dra {} -dre {} -l {} -r {} -pwr {} -auto {}".format(python, script, area_side_size, run, lora_devices,
                                                                                                                                                lora_e_devices, time, step, interval, position_mode, time_mode, dr_allocation_mode, 
                                                                                                                                                payload_size, LoRa_DR, LoRaE_DR, log_file, random, devices_tx_power, dr_auto_select)
    os.system(command)
    
    if os.path.exists(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'):
        os.remove(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log')
    '''
    try:
        metrics = np.load(result_file.format(lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload, run)+result_ext, allow_pickle=True)
    except FileNotFoundError:
        return (-1,-1,-1,-1,-1,-1,-1,-1,-1,-1)
    else:
        os.remove(result_file.format(lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload, run)+result_ext)
        return (lora_devices, lora_e_devices, f'{run}/{runs}', LoRa_DR, LoRaE_DR, payload, metrics[0], metrics[1], metrics[2], metrics[3])
    '''
   
if __name__ == '__main__':
    
    LoRa_DR_list = list(map(int, config.get('LoRa', 'LoRa_data_rates').split(','))) 
    LoRaE_DR_list = list(map(int, config.get('LoRa_E', 'LoRa_E_data_rates').split(',')))
    n_lora_devices =  list(map(int, config.get('LoRa', 'n_LoRa_devices').split(',')))
    n_lora_e_devices = list(map(int, config.get('LoRa_E', 'n_LoRa_E_devices').split(',')))
    #assert len(n_lora_devices) == len(n_lora_e_devices), 'LoRa and LoRa-E num devices lists are not the same length'
    p = Pool(os.cpu_count())
    args = [(run+1, lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR) for lora_devices in n_lora_devices 
                                                                              for lora_e_devices in n_lora_e_devices 
                                                                              for LoRa_DR in LoRa_DR_list
                                                                              for LoRaE_DR in LoRaE_DR_list
                                                                              for run in range(num_runs)]
    p.starmap(run_simulation, iterable=args, chunksize=1)
    p.close()
    #df = pd.DataFrame(results, columns=['N_lora_devices','N_lora_e_devices','run', 'LoRa_DR', 'LR-FHSS_DR', 'payload', 'LoRa_RX_pkts', 'LoRa_gen_pkts', 'LR-FHSS_RX_pkts', 'LR-FHSS_gen_pkts'])
    #df.to_csv('results/results.csv')