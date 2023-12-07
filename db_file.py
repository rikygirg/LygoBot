import json
import os

absolute_path = os.path.dirname(__file__)


class Database(dict):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        try:
            with open(os.path.join(absolute_path, self.file_name), 'r') as f:
                data = json.load(f)
                self.update(data)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            value = input(f"Key {key} not found, please enter a value: ")
            self[key] = value
            return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save()

    def save(self):
        with open(os.path.join(absolute_path, self.file_name), 'w') as f:
            json.dump(self, f)
