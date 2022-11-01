import argparse
import textwrap
import requests
import json
import urllib3
import time
import sys
import yaml


yaml_file = "nxapi.yaml"

def read_yaml(yaml_file):
    try:
        fd = open(yaml_file)
    except FileNotFoundError:
        print("YAML file doesn't exist!\n")
    else:
        yaml_dict = yaml.load(fd, Loader=yaml.FullLoader)
        fd.close()
        return yaml_dict


yaml_output = read_yaml(yaml_file)

# for x in yaml_output:
print(type(yaml_output))
print(yaml_output["user"])
