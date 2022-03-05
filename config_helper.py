import json

class ConfigHelper():
    def load_config():
        try:
            with open('config.json') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise SystemExit('Unable to open the config file')

    def save_config(config):
        try:
            with open('config.json', 'w') as outfile:
                json.dump(config, outfile, indent=2)
        except PermissionError:
            raise PermissionError('Permission denied')

