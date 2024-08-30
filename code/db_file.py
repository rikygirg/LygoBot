import json
import os

absolute_path = os.path.dirname(__file__)

class Database(dict):
    def __init__(self, file_name, persist=True):
        """
        Initialize the database.
        :param file_name: Name of the file to store data.
        :param persist: Boolean flag to control whether to persist data to the file.
        """
        super().__init__()
        self.file_name = file_name
        self.persist = persist  # Control whether to persist data to file

        if self.persist:
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
            if key == "K_HEIGHT":
                self[key] = 10
                return 10
            value = input(f"Key {key} not found, please enter a value: ")
            self[key] = value
            return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self.persist:  # Save to file only if persist is True
            self.save()

    def save(self):
        if self.persist:  # Check if data should be persisted
            with open(os.path.join(absolute_path, self.file_name), 'w') as f:
                json.dump(self, f)

