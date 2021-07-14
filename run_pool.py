"""
Received frames vs number of devices @ maximum transmission rate
"""
import os
from struct import Struct
import pandas as pd
from multiprocessing import Pool
import multiprocessing as mp
import numpy as np
import subprocess
from ctypes import Structure, c_int, c_float


python = "python3"
script = "Simulator.py"

result_file = './results/{}_{}_{}_{}_{}_{}_'
result_ext = ".npy"

runs = 2
LoRa_DR = 0  # 0 to 5 is LoRa; 8 to 11 is LoRa-E
LoRaE_DR = 8
payload = 15
n_devices = [100]#[10, 100, 1000, 10000]
n_percentages = [0.0,1.0]#[range(0,100,10)]

def run_simulation(run, device, payload, percentage, LoRa_DR, LoRaE_DR):
    print('Running test with parameters devices={}, percentage={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format( device,
                                                                                                                            percentage,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload,
                                                                                                                            run + 1,
                                                                                                                            runs))
    log_file = result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)+'.log'
    command = "{} {} -n {} -d {} -pl {} -p {} -dra {} -dre {} -l {}".format(python, script, run, device,
                                                                            payload, percentage, LoRa_DR, 
                                                                            LoRaE_DR, log_file)
    os.system(command)
    
    metrics = np.load(result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)+result_ext, allow_pickle=True)
    os.remove(result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)+result_ext)
    return (device, percentage, f'{run}/{runs}', LoRa_DR, LoRaE_DR, payload, metrics[0], metrics[1], metrics[2], metrics[3])
   
    

if __name__ == '__main__':
    
    
    #manager = Manager()
    #results = manager.list([[0,0,0,0,0,0,0,0,0,0]]*len(n_devices)*len(n_percentages)*runs)
    #results = Array()
    #results.extend([0,0,0,0,0,0,0,0,0,0]*len(n_devices)*len(n_percentages)*runs)
    
    p = Pool(os.cpu_count())
    
    results = []
    for device in n_devices:
        # Execute for all devices
        for percentage in n_percentages:
            # Repeat for number of runs
            result = p.starmap(run_simulation, iterable=[(run, device, payload, percentage, LoRa_DR, LoRaE_DR) for run in range(runs)])
            results.extend(result)

    df = pd.DataFrame(results, columns=['N_devices','percentage','run', 'LoRa_DR', 'LR-FHSS_DR', 'payload', 'LoRa_RX_pkts', 'LoRa_gen_pkts', 'LR-FHSS_RX_pkts', 'LR-FHSS_gen_pkts'])
    df.to_csv('results/results.csv')