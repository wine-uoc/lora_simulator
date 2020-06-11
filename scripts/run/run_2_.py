"""
Received frames vs number of devices @ maximum transmission rate
"""
import os

python = "python3"
script = "Simulator.py"

result_file = './results/dr{}/pl{}/{}_max_{}'
result_ext = ".npy"

runs = 10
datarates = [1]  # 0 to 5 is LoRa; 8 to 11 is LoRa-E
payloads = [50]
devices_lora = []
devices_lora.extend(list(range(1, 511, 10)))
devices_loraE = []

# Execute for all datarates
for datarate in datarates:
    # Adjust device granularity according to DR
    if datarate < 8:
        devices = devices_lora
    else:
        devices = devices_loraE
    # Execute for all payloads
    for payload in payloads:
        # Execute for all devices
        for device in devices:
            # Repeat for number of runs
            for i in range(runs):
                data_file = result_file.format(datarate, payload, device, i) + result_ext
                log_file = result_file.format(datarate, payload, device, i)
                # Check if already simulated
                if os.path.isfile(data_file):
                    print('Skipping test {} as results already exist!'.format(data_file))
                # Execute the simulation by calling the Simulator.py with the appropriate parameters
                else:
                    print(
                        'Running test with parameters datarate={}, payload={}, devices={}, runs={}/{}.'.format(datarate,
                                                                                                               payload,
                                                                                                               device,
                                                                                                               i + 1,
                                                                                                               runs))
                    command = "{} {} -r {} -d {} -tm {} -pl {} -dr {} -l {}".format(python, script, i, device, 'max',
                                                                                    payload, datarate, log_file)
                    os.system(command)
