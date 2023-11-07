import json
import os

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QFileDialog


class Serializer:
    """
    Class that performs operations with file system
    """

    def __init__(self):
        self.recent_directory = None
        self.current_file = None

        self.reg_file = QSettings('settings.ini', QSettings.Format.IniFormat)
        self.file_extension = '.dg'
        self.program_name = 'Descriptive Geometry'

    def serialize(self, content, path='history.txt'):
        """
        Function to serialize the content to the file.
        :param content: content to serialize
        :param path: path to the file
        """

        # Serializing
        try:
            hist = json.dumps(content)  # TODO: exception is generated if content is not a valid object
        except Exception:
            raise ValueError('File can not be encoded with JSON.')

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
        """
        Function to fix extension of the given file
        :param path: path to a file
        :return: path to a file with fixed extension
        """

        if '.' not in path:
            return path + self.file_extension
        return (path[:path.rindex('.')] + self.file_extension) if '.' in path else (path + self.file_extension)

    def serialize_file(self, parent, create_new=False, content=None):
        """
        Function to serialize the given content
        :param parent: widget to be a parent of QFileDialog
        :param create_new: current file is used if True else QFileDialog is opened
        :param content: JSON-serializable object or serialized one
        :return: path to a file
        """

        if create_new or not self.current_file:
            path = self.extension(QFileDialog.getSaveFileName(parent, 'Select File Name', self.recent_directory,
                                                              f'{self.program_name} Files (*{self.file_extension})')[0])
        else:
            path = self.current_file

        if path:
            self.serialize(content, path)
            self.current_file = path
        else:
            raise FileNotFoundError('File is not chosen.')
        return path

    def deserialize_file(self, parent, path, deserialization_func):
        """
        Function to deserialize the given file
        :param parent: widget to be a parent of QFileDialog
        :param path: path to a file (QFileDialog is opened if None)
        :param deserialization_func: function to process deserialized objects
        :return:
        """

        if not path:
            path = QFileDialog.getOpenFileName(parent, 'Open File', self.recent_directory,
                                               f'{self.program_name} Files (*{self.file_extension})')[0]
        if path and os.path.isfile(path):
            dct = self.deserialize(path)
            if dct:
                try:
                    deserialization_func(dct)
                except Exception as e:
                    raise ValueError(f'Invalid file: {dct}. Error: {e}.')
                else:
                    self.current_file = path
            else:
                raise ValueError('File can not be decoded with JSON.')
        else:
            raise FileNotFoundError('File is not chosen.')

    def new_file(self):
        self.current_file = None


if __name__ == '__main__':
    srl = Serializer()
    while inp := input():
        print(srl.extension(inp))
