import yaml
import pprint
import pydoc


stream = open('Simulator.yaml', 'r')
dict = yaml.load(stream=stream, Loader=yaml.Loader)

area_side_size = dict['common']['area_side_size']
time = dict['common']['time']
step = dict['common']['step']
lora_dr = dict['LoRa']['LoRa_data_rates']

pprint.pprint(type(lora_dr))