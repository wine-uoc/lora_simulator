"""
Received frames vs number of devices @ maximum transmission rate
"""
import os
from multiprocessing import Pool
import yaml

python = "python3"
script = "Simulator.py"
config_file = "Simulator.yaml"

config = yaml.load(open(config_file), Loader=yaml.Loader)

result_file = '{}/{}_{}_{}_{}_{}_{}_'
result_ext = ".npy"

area_side_size = config['common']['area_side_size']
time = config['common']['time']
step = config['common']['step']
interval = config['common']['interval']
position_mode = config['common']['position_mode']
position_mode_values = config['common']['position_mode_values']
time_mode = config['common']['time_mode']
payload_size = config['common']['payload_size']
random = config['common']['random']
devices_tx_power = config['common']['devices_tx_power']
use_ratios=config['common']['use_ratios']
LoRa_ratios=config['common']['LoRa_ratios']
num_total_devices=config['common']['num_total_devices']
num_runs = config['common']['num_runs']
dr_auto_select = config['set_1']['LoRa_auto_DR_selection']

def run_simulation_no_ratios(run, lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR):
    

    print('Running test with parameters set_1_devices={}, set_2_devices={}, set_1_DR={}, set_2_DR={}, payload={}, runs={}/{}.'.format(lora_devices,
                                                                                                                            lora_e_devices,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload_size,
                                                                                                                            run,
                                                                                                                            num_runs))
    log_file = result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'
    command = "{} {} -s {} -n {} -ur {} -d1 {} -d2 {} -t {} -st {} -i {} -pm {} -pmv {} -tm {} -pl {} -dr1 {} -dr2 {} -l {} -r {} -pwr {} -auto {}".format(python, script, area_side_size, run, use_ratios, lora_devices, lora_e_devices, 
                                                                                                                                                time, step, interval, position_mode, position_mode_values, time_mode, 
                                                                                                                                                payload_size, LoRa_DR, LoRaE_DR, log_file, random, devices_tx_power, 
                                                                                                                                                dr_auto_select)
    os.system(command)
    
    if os.path.exists(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'):
        os.remove(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log')
   
def run_simulation_ratios (run, lora_ratio, num_devices, LoRa_DR, LoRaE_DR):
    print('Running test with parameters lora_devices={}, lora_e_devices={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format(lora_ratio,
                                                                                                                            num_devices,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload_size,
                                                                                                                            run,
                                                                                                                            num_runs))
    log_file = result_file.format(config['common']['root_dir_name'], lora_ratio, num_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'
    command = "{} {} -s {} -n {} -ur {} -lr {} -d {} -t {} -st {} -i {} -pm {} -pmv {} -tm {} -pl {} -dr1 {} -dr2 {} -l {} -r {} -pwr {} -auto {}".format(python, script, area_side_size, run, use_ratios, lora_ratio, num_devices, 
                                                                                                                                                time, step, interval, position_mode, position_mode_values, time_mode, 
                                                                                                                                                payload_size, LoRa_DR, LoRaE_DR, log_file, random, devices_tx_power, 
                                                                                                                                                dr_auto_select)
    os.system(command)
    
    if os.path.exists(result_file.format(config['common']['root_dir_name'], lora_ratio, num_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'):
        os.remove(result_file.format(config['common']['root_dir_name'], lora_ratio, num_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log')
   


if __name__ == '__main__':
    
    data_rates_set_1 = config['set_1']['data_rates_set_1'] 
    data_rates_set_2 = config['set_2']['data_rates_set_2']
    n_devices_set_1 = config['set_1']['n_devices_set_1']
    n_devices_set_2 = config['set_2']['n_devices_set_2']
   
    p = Pool(os.cpu_count())

    if use_ratios == 0:
        # Use explicit amount of LoRa/LoRa-E devices for each simulation 
        args = [(run+1, devices_set_1, devices_set_2, data_rate_set_1, data_rate_set_2) for devices_set_1 in n_devices_set_1 
                                                                                        for devices_set_2 in n_devices_set_2 
                                                                                        for data_rate_set_1 in data_rates_set_1
                                                                                        for data_rate_set_2 in data_rates_set_2
                                                                                        for run in range(num_runs)]
        p.starmap(run_simulation_no_ratios, iterable=args, chunksize=1)
    else:
        # Apply ratio to a total amount of devices for each simulation.
        args = [(run+1, lora_ratio, num_devices, LoRa_DR, LoRaE_DR) for lora_ratio in LoRa_ratios
                                                                        for num_devices in num_total_devices
                                                                        for LoRa_DR in data_rates_set_1
                                                                        for LoRaE_DR in data_rates_set_2
                                                                        for run in range(num_runs)]
        p.starmap(run_simulation_ratios, iterable=args, chunksize=1)
    p.close()
    