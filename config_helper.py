import json

class ConfigHelper():
    def load_config():
        with open('config.json') as json_file:
            return json.load(json_file)

    def save_config(config):
        with open('config.json', 'w') as outfile:
            json.dump(config, outfile, indent=2)
