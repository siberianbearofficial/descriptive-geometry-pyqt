import utils.history.serializer as srl
import os


class SettingsManager:
    def __init__(self):
        try:
            dct = srl.deserialize(path='settings.txt')
        except Exception:
            dct = dict()
        self.recent_files = dct.get('recent_files', [])
        if not isinstance(self.recent_files, list):
            self.recent_files = []
        self.recent_directory = dct.get('recent_directory')
        if not isinstance(self.recent_directory, str) or not os.path.isdir(self.recent_directory):
            self.recent_directory = os.getcwd()

    def add_to_recent_files(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        if len(self.recent_files) > 8:
            self.recent_files = self.recent_files[:8]

    def set_recent_directory(self, path):
        self.recent_directory = os.path.dirname(path)

    def serialize(self):
        dct = {'recent_files': self.recent_files, 'recent_directory': self.recent_directory}
        srl.serialize(dct, path='settings.txt')
