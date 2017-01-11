import os
import collections

import yaml



def read_yaml(yaml_path):
    with open(yaml_path,'r') as fp:
        data = yaml.safe_load(fp)
    return data


def write_yaml(data, yaml_path):
    yaml.safe_dump(data, yaml_path)


def spreadsheet_keyvalue_generator(spreadsheet_path):
    print(spreadsheet_path)






