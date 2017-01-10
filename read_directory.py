import yaml
import os





def read_directory(loc='/Users/steve/jan2017A'):
    return {'db_spec': None, 'open_spreadsheets': None, 'mirrored_spreadsheets': None}


def read_yaml(yaml_path):
    with open(yaml_path,'r') as fp:
        data = yaml.safe_load(fp)
    return data


def write_yaml(data, yaml_path):
    yaml.safe_dump(data, yaml_path)





