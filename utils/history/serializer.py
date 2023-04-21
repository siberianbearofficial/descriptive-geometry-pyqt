import json
import os

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog


class Serializer:
    def __init__(self):
        self.reg_file = QSettings('settings.ini', QSettings.IniFormat)
        self.file_extension = '.dg'

    def serialize(self, content, path='history.txt'):
        """
        Function to serialize the content to the file.
        :param content: content to serialize
        :param path: path to the file
        """

        # Serializing
        hist = json.dumps(content)  # TODO: exception is generated if content is not a valid object

        # Writing json
        if path == 'history.txt':
            self.reg_file.setValue('history', hist)
        elif path == 'settings.txt':
            self.reg_file.setValue('settings', hist)
        else:
            print(hist, file=open(path, 'w', encoding='utf-8'), end='')

    def deserialize(self, path='history.txt'):
        """
        Function to deserialize the content of the given file.
        :param path: path to the file
        """

        # Getting raw content
        if path == 'history.txt':
            hist = self.reg_file.value('history', defaultValue='{}')
        elif path == 'settings.txt':
            hist = self.reg_file.value('settings', defaultValue='{}')
        else:
            hist = open(path, encoding='utf-8').read()

        # Deserializing
        try:
            dct = json.loads(hist)
        except ValueError:
            dct = dict()
        return dct

    def extension(self, path: str):
        if '.' not in path:
            return path + self.file_extension
        return (path[:path.rindex('.')] + self.file_extension) if '.' in path else (path + self.file_extension)

    def deserialize_file(self, parent, path, directory, deserialization_func):
        if not path:
            path = QFileDialog.getOpenFileName(parent, 'Open File', directory,
                                               'Descriptive Geometry Files (*.dg)')[0]
        if path and os.path.isfile(path):
            dct = self.deserialize(path)
            if dct:
                try:
                    deserialization_func(dct)
                except Exception as e:
                    raise ValueError(f'Invalid file: {dct}. Error: {e}.')
            else:
                raise ValueError('File can not be decoded with JSON.')
        else:
            raise FileNotFoundError('File is not chosen.')


if __name__ == '__main__':
    srl = Serializer()
    while inp := input():
        print(srl.extension(inp))
