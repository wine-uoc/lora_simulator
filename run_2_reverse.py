import os

# Received frames vs number of devices @ maximum transmission rate

runs = 2
pls = [10, 50]
drs = [9]     # 0, 5 is LoRa; 8, 11 is LoRa-E


for dr in drs:
    for pl in pls:
        for devices in range(1, 4001, 10):
            for i in range(runs):
                # check if already simulated
                f_name = './results/dr' + str(dr) + '/pl' + str(pl) + '/' + str(devices) + '_max_' + str(i) + '.npy'
                if os.path.isfile(f_name):
                    print('Skipping ...')
                    print(f_name)
                else:
                    os.system('python3 Test.py' +
                              ' -r ' + str(i) +
                              ' -d ' + str(devices) +
                              ' -tm ' + 'max' +
                              ' -pl ' + str(pl) +
                              ' -dr ' + str(dr)
                              )
