import yaml
import os

def read_config():
    config_path = os.getenv("CONFIG_PATH")
    if not config_path:
        raise ValueError("CONFIG_PATH environment variable is not set.")

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
