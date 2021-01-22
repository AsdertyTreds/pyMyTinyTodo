import json


class MttSettings:
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.values = json.loads(f.read())

    def save(self, config_file):
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.values, f, indent=4, sort_keys=True)
