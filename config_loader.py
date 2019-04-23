import sys
import json
import yaml

def load(config_file, type):
    file_name = config_file
    try:
        if type == 'json':
            file_name += '.json'
            with open(file_name, 'r') as cfg_file:
                return json.load(cfg_file)
        elif type == 'yaml':
            file_name += '.yaml'
            with open(file_name, 'r') as cfg_file:
                return yaml.full_load(cfg_file)
        else:
            raise Exception('Invalid config type: [{}]'.format(type))
    except Exception:
        raise Exception('Invalid config file: [{}]'.format(file_name))
        