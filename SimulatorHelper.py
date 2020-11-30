import os

import Device
import Sequence


def create_save_dir(options):
    """Create a directory to save the results"""
    if options.percentage == 1:
        dir_name = './results/dr' + str(options.data_rate_lora) + '/pl' + str(options.payload) + '/'
    elif options.percentage == 0:
        dir_name = './results/dr' + str(options.data_rate_lora_e) + '/pl' + str(options.payload) + '/'
    else:
        dir_name = './results/p' + str(options.percentage) + '/pl' + str(options.payload) + '/'

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    return dir_name

def create_devices(
    parameter_list,             # parameters defined by LoRaWAN
    num_devices,
    data_rate,
    time_mode,
    tx_interval,
    tx_payload,
    offset_id=0,                # value to start id counter 
    pre_compute_seq=False,      # option to use a pre-computed f.h. sequence or compute it online
    sim_duration=3600000,       # needed to pre-compute the number of hops in advance
    gateway=None                # the gateway, to compute relative distance and assign a DR
):
    """
    docstring
    """
    (
        device_modulation,
        simulation_channels,
        device_tx_rate,
        number_repetitions_header,
        numerator_coding_rate,
        hop_duration,
    ) = parameter_list

    if data_rate > 7 and pre_compute_seq:
        # LoRa-E needs a frequency hopping pattern that can be pre-computed
        if tx_interval == 'max':
            # we can use the number of transmissions to pre-allocate memory
            # +++ TODO +++: calculate this exactly
            max_hops = sim_duration / 4000 * hop_duration
        else:
            max_hops = sim_duration / tx_interval * hop_duration

        seqs = Sequence.Sequence(modulation = device_modulation,
                                n_devices  = num_devices,
                                n_bits     = 9,
                                n_channels = simulation_channels,
                                n_hops     = max_hops,
                                seq_type   = 'lora-e-eu-hash',
                                dr         = data_rate)

    # Create LoRaWAN devices of specific type 
    device_list = []

    for device_id in range(num_devices):
        device = Device.Device(device_id      = device_id + offset_id,
                               time_mode      = time_mode,
                               tx_interval    = tx_interval,
                               tx_rate        = device_tx_rate,
                               tx_payload     = tx_payload,
                               modulation     = device_modulation,
                               numerator_cr   = numerator_coding_rate,
                               hop_duration   = hop_duration if data_rate > 7 else None,
                               hop_list       = seqs.get_hopping_sequence(device_id) if pre_compute_seq else None,
                               num_rep_header = number_repetitions_header,
                               dr             = data_rate,
                               gateway        = gateway)
        device_list.append(device)

    return device_list
