import json

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
    
    return config

