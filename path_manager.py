import json
import os

class PathManager:
    def __init__(self, folder_path='.venv/path_different.json'):
        folder_path = os.path.join(os.getcwd(), folder_path)
        with open(folder_path) as f:
            data = json.load(f)
        self.site_folder = data["site_folder"]
        self.bot_folder = os.getcwd()

    @property
    def site_logs(self):
        if self.site_folder:
            path = os.path.join(self.site_folder, 'Logs')
            return path
        else:
            raise ValueError("Site folder path is not defined.")

    @property
    def site_json(self):
        if self.site_folder:
            path = os.path.join(self.site_folder, 'Json')
            return path
        else:
            raise ValueError("Site folder path is not defined.")

    @property
    def site_wallet(self):
        if self.site_folder:
            path = os.path.join(self.site_folder, 'Wallet')
            return path
        else:
            raise ValueError("Site folder path is not defined.")


