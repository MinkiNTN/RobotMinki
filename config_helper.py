import json

class ConfigHelper():
    def load_config():
        try:
            with open('config.json') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise SystemExit('Config file not found')
        except json.JSONDecodeError:
            raise SystemExit('Unable to open the config file')

    def save_config(config):
        try:
            with open('config.json', 'w') as outfile:
                json.dump(config, outfile, indent=2)
        except PermissionError:
            raise PermissionError('Permission denied')
            
    """
    Check if a specific ID is in the whitelist
    To allow all, leave the list empty.
    """
    def id_is_in_whitelist(id, list):
        if list:
            if list.count(id):
                return True
            else:
                return False
        else:
            return True
