import os
import json
import subprocess
import configparser

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(_MODULE_DIR, '..', 'config.ini'))

    config['settings']['AZURE_CLI_PATH'] = os.path.expanduser(config['settings']['AZURE_CLI_PATH'])

    return config['settings']
