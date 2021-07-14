"""
Received frames vs number of devices @ maximum transmission rate
"""
import os
from struct import Struct
import pandas as pd
from multiprocessing import Process, Manager, Array
import multiprocessing as mp
import numpy as np
import subprocess
from ctypes import Structure, c_int, c_float

class Record(Structure):
    _fields_ = [('device')]
python = "python3"
script = "Simulator.py"

result_file = './results/{}_{}_{}_{}_{}_{}_'
result_ext = ".npy"

runs = 1
LoRa_DR = 0  # 0 to 5 is LoRa; 8 to 11 is LoRa-E
LoRaE_DR = 8
payload = 50
n_devices = [10, 100]#[10, 100, 1000, 10000]
n_percentages = [0.0]#[range(0,100,10)]

def run_simulation(results, run, device, payload, percentage, LoRa_DR, LoRaE_DR, idx):
    print('Running test with parameters devices={}, percentage={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format( device,
                                                                                                                            percentage,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload,
                                                                                                                            run + 1,
                                                                                                                            runs))
    log_file = result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)
    command = "{} {} -n {} -d {} -pl {} -p {} -dra {} -dre {} -l {}".format(python, script, run, device,
                                                                            payload, percentage, LoRa_DR, 
                                                                            LoRaE_DR, log_file)
    os.system(command)
    
    metrics = np.load(result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)+result_ext, allow_pickle=True)
    results[idx][0] = device
    results[idx][1] = percentage
    results[idx][2] = f'{run}/{runs}'
    results[idx][3] = LoRa_DR
    results[idx][4] = LoRaE_DR
    results[idx][5] = payload
    results[idx][6] = metrics[0]
    results[idx][7] = metrics[1]
    results[idx][8] = metrics[2]
    results[idx][9] = metrics[3]
    #os.remove(result_file.format(device, percentage, LoRa_DR, LoRaE_DR, payload, run)+result_ext)
    

if __name__ == '__main__':
    
    
    #manager = Manager()
    #results = manager.list([[0,0,0,0,0,0,0,0,0,0]]*len(n_devices)*len(n_percentages)*runs)
    #results = Array()
    print(results)
    #results.extend([0,0,0,0,0,0,0,0,0,0]*len(n_devices)*len(n_percentages)*runs)
    idx = 0
    for device in n_devices:
        # Execute for all devices
        for percentage in n_percentages:
            # Repeat for number of runs
            processes = []
            for run in range(runs):
                p = mp.Process(target=run_simulation, args=(results, run, device, payload, percentage, LoRa_DR, LoRaE_DR, idx))
                processes.append(p)
                idx += 1

            for p in processes:
                p.start()

            for p in processes:
                p.join()

    print(results)