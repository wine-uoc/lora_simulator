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
num_runs = config['common']['num_runs']
dr_auto_select = config['LoRa']['LoRa_auto_DR_selection']

def run_simulation(run, lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR):
    

    print('Running test with parameters lora_devices={}, lora_e_devices={}, LoRa_DR={}, LoRa-E_DR={}, payload={}, runs={}/{}.'.format(lora_devices,
                                                                                                                            lora_e_devices,
                                                                                                                            LoRa_DR,
                                                                                                                            LoRaE_DR,
                                                                                                                            payload_size,
                                                                                                                            run,
                                                                                                                            num_runs))
    log_file = result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'
    command = "{} {} -s {} -n {} -da {} -de {} -t {} -st {} -i {} -pm {} -pmv {} -tm {} -pl {} -dra {} -dre {} -l {} -r {} -pwr {} -auto {}".format(python, script, area_side_size, run, lora_devices, lora_e_devices, 
                                                                                                                                                time, step, interval, position_mode, position_mode_values, time_mode, 
                                                                                                                                                payload_size, LoRa_DR, LoRaE_DR, log_file, random, devices_tx_power, 
                                                                                                                                                dr_auto_select)
    os.system(command)
    
    if os.path.exists(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log'):
        os.remove(result_file.format(config['common']['root_dir_name'], lora_devices, lora_e_devices, LoRa_DR, LoRaE_DR, payload_size, run)+'.log')
   
if __name__ == '__main__':
    
    LoRa_DR_list = config['LoRa']['LoRa_data_rates'] 
    LoRaE_DR_list = config['LoRa_E']['LoRa_E_data_rates']
    n_lora_devices = config['LoRa']['n_LoRa_devices']
    n_lora_e_devices = config['LoRa_E']['n_LoRa_E_devices']
   
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