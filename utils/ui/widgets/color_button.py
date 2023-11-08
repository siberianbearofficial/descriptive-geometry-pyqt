from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QDialog, QMenu, QGridLayout

from utils.color import *


class ColorButton(QPushButton):
    colorChanged = pyqtSignal(ObjectColor)

    def __init__(self, theme_manager, color: ObjectColor = RANDOM_COLOR, _random=False, layer=False, other=False):
        super().__init__()
        self.color = color
        self._theme_manager = theme_manager
        self.clicked.connect(self._on_clicked)

        self.random = _random
        self.layer = layer
        self.other = other

    def _on_clicked(self):
        window = ColorWindow(self._theme_manager, self.random, self.layer, self.other)
        window.move(self.mapToGlobal(QPoint(0, self.height() + 5)))
        window.exec()
        if window.color is not None:
            self.color = window.color
            self.colorChanged.emit(self.color)
        self.set_styles()

    def set_color(self, color):
        self.color = color
        self.set_styles()

    def set_styles(self):
        if self.color.type == ObjectColor.RANDOM or self.color.type == ObjectColor.FROM_LAYER:
            self._theme_manager.auto_css(self, palette='Main')
            self.setIcon(QIcon(self._theme_manager.get_image('random')))
            return
        self.setIcon(QIcon())
        if self.color.type == ObjectColor.STANDARD:
            color = self._theme_manager['Colors'][self.color.color]
        else:
            color = self.color.color
        self.setStyleSheet(self._theme_manager.button_css(palette='Main').replace(
            self._theme_manager['MainColor'], color).replace(
            self._theme_manager['MainHoverColor'], color))


class ColorWindow(QMenu):
    def __init__(self, tm, _random=False, layer=False, other=False):
        super().__init__()
        self.tm = tm
        self.color = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(main_layout)

        self._button_random = QPushButton("Случайный")
        self._button_random.setFixedHeight(22)
        self._button_random.clicked.connect(lambda: self.return_color(RANDOM_COLOR))
        if not _random:
            self._button_random.hide()
        main_layout.addWidget(self._button_random)

        self._button_layer = QPushButton("Цвет слоя")
        self._button_layer.setFixedHeight(22)
        self._button_layer.clicked.connect(lambda: self.return_color(LAYER_COLOR))
        if not layer:
            self._button_layer.hide()
        main_layout.addWidget(self._button_layer)

        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)
        self._color_buttons = []

        for i in range(12):
            button = QPushButton()
            button.setFixedSize(32, 22)
            self.connect_button(button, i)
            self._color_buttons.append(button)
            grid_layout.addWidget(button, i // 4, i % 4)

    def return_color(self, color):
        self.color = color
        self.close()

    def connect_button(self, button, i):
        button.clicked.connect(lambda: self.return_color(ObjectColor(i, ObjectColor.STANDARD)))

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self.set_styles()

    def set_styles(self):
        self.tm.auto_css(self)
        for el in [self._button_random, self._button_layer]:
            self.tm.auto_css(el, border=False)
        for i in range(12):
            self._color_buttons[i].setStyleSheet(self.tm.button_css(palette='Main').replace(
                self.tm['MainColor'], self.tm['Colors'][i]).replace(
                self.tm['MainHoverColor'], self.tm['Colors'][i]))
