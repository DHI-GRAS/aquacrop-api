#!/usr/bin/env python
import subprocess
from deployment_config import parse_config

exclude_keys = ['azure_cli_path', 'azure_subscription']


def set_functionapp_env_variables(config):
    az = config['AZURE_CLI_PATH']
    group_name = config['AZURE_GROUP_NAME']
    app_name = config['AZURE_FUNCTION_APP_NAME']

    settings = ''
    for key in config:
        print(key)
        if key not in exclude_keys:
            settings += f'{key.upper()}={config[key]} '
    bash_command = (
        f'{az} functionapp config appsettings set -n {app_name} -g {group_name} '
        f'--settings {settings}')
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error is not None:
        raise ValueError(error)
    return settings


if __name__ == '__main__':

    print('Reading config.ini ...')
    config = parse_config()

    print('Setting functionapp environment variables ...')
    settings = set_functionapp_env_variables(config)

    print(f'Set environment variables: {settings}')
