import utils.history.serializer as srl


class SettingsManager:
    def __init__(self):
        try:
            dct = srl.deserialize(path='settings.txt')
        except Exception:
            dct = dict()
        print(dct)
        self.recent_files = dct.get('recent_files', [])
        if not isinstance(self.recent_files, list):
            self.recent_files = []

    def add_to_recent_files(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        if len(self.recent_files) > 8:
            self.recent_files = self.recent_files[:8]

    def serialize(self):
        dct = {'recent_files': self.recent_files}
        srl.serialize(dct, path='settings.txt')
