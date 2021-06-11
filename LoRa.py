from Device import Device

class LoRa(Device):
    
    def __init__(self, device_id, time_mode, tx_interval, tx_rate, tx_payload, modulation, numerator_cr, hop_duration, hop_list, num_rep_header, dr, gateway):
        super().__init__(device_id=device_id, time_mode=time_mode, tx_interval=tx_interval, tx_rate=tx_rate, tx_payload=tx_payload, modulation=modulation, numerator_cr=numerator_cr, hop_duration=hop_duration, hop_list=hop_list, num_rep_header=num_rep_header, dr=dr, gateway=gateway)