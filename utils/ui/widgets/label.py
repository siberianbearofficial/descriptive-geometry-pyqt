from PyQt6.QtCore import pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel

from utils.color import Color


class Label(QLabel):
    colorChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = QColor(0, 0, 0)
        self.setStyleSheet(f'color: {Color(self._color)};')
        self.colorChanged.connect(self._color_changed)

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

    def setColor(self, color: Color):
        self.color = QColor(color)

    def _color_changed(self):
        self.setStyleSheet(f'color: {Color(self._color)};')
