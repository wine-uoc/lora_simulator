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

runs = 2
LoRa_DR_list = [0, 1]  # 0 to 5 is LoRa; 8 to 11 is LoRa-E
LoRaE_DR_list = [8, 9]
payload = 10
n_lora_devices = [10]#[50, 50, 50, 50, 50, 50, 50, 50, 50]
n_lora_e_devices = [1, 2, 3, 4, 5]#[1, 5, 10, 50, 100, 500, 1000, 5000, 10000] 
#n_percentages = [0.0, 1.0]

def run_simulation(run, lora_devices, lora_e_devices, payload, LoRa_DR, LoRaE_DR):
    print('Running test with parameters lora_devices={}, lora_e_devices={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format(lora_devices,
                                                                                                                            lora_e_devices,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload,
                                                                                                                            run,
                                                                                                                            runs))
    log_file = result_file.format(config['simulator']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload, run)+'.log'
    command = "{} {} -n {} -da {} -de {} -pl {} -dra {} -dre {} -l {}".format(python, script, run, lora_devices,
                                                                            lora_e_devices, payload, LoRa_DR, 
                                                                            LoRaE_DR, log_file)
    os.system(command)
    
    if os.path.exists(result_file.format(config['simulator']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload, run)+'.log'):
        os.remove(result_file.format(config['simulator']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload, run)+'.log')
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
    
    #assert len(n_lora_devices) == len(n_lora_e_devices), 'LoRa and LoRa-E num devices lists are not the same length'
    p = Pool(os.cpu_count())
    args = [(run+1, lora_devices, lora_e_devices, payload, LoRa_DR, LoRaE_DR) for lora_devices in n_lora_devices 
                                                                              for lora_e_devices in n_lora_e_devices 
                                                                              for LoRa_DR in LoRa_DR_list
                                                                              for LoRaE_DR in LoRaE_DR_list
                                                                              for run in range(runs)]
    p.starmap(run_simulation, iterable=args, chunksize=1)
    p.close()
    #df = pd.DataFrame(results, columns=['N_lora_devices','N_lora_e_devices','run', 'LoRa_DR', 'LR-FHSS_DR', 'payload', 'LoRa_RX_pkts', 'LoRa_gen_pkts', 'LR-FHSS_RX_pkts', 'LR-FHSS_gen_pkts'])
    #df.to_csv('results/results.csv')