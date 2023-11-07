from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QMenu, QWidget

from utils.ui.widgets.button import Button


class DrawTool(QWidget):
    ICON_SIZE = 30

    def __init__(self, theme_manager, struct):
        super().__init__()
        self.theme_manager = theme_manager

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.button = Button(self.theme_manager, tuple(struct.values())[0][0],
                             css='Menu', tooltip=tuple(struct.keys())[0])
        self.button.setFixedSize(DrawTool.ICON_SIZE, DrawTool.ICON_SIZE)
        self.button.clicked.connect(tuple(struct.values())[0][1])
        layout.addWidget(self.button)

        self.arrow = Button(self.theme_manager, 'right_arrow', css='Menu')
        self.arrow.setFixedSize(12, DrawTool.ICON_SIZE)
        self.arrow.clicked.connect(self.run_menu)
        layout.addWidget(self.arrow)

        self.menu = DrawToolMenu(self.theme_manager, struct)

    def run_menu(self):
        self.menu.move(self.mapToGlobal((self.arrow.pos()) + QPoint(15, 0)))
        self.menu.exec()

    def set_styles(self):
        self.button.set_styles()
        self.arrow.set_styles()
        self.menu.set_styles()
        self.button.setStyleSheet(self.theme_manager.button_css(palette='Menu', border=False, br_right=False))
        self.arrow.setStyleSheet(self.theme_manager.button_css(palette='Menu', border=False, br_left=False))


class DrawToolMenu(QMenu):
    def __init__(self, theme_manager, struct):
        super().__init__()
        self.theme_manager = theme_manager
        self.struct = struct
        self.actions = dict()

        for key, item in struct.items():
            action = self.addAction(key)
            self.actions[key] = action
            action.triggered.connect(item[1])

    def set_styles(self):
        self.theme_manager.auto_css(self)
        for key, item in self.actions.items():
            item.setIcon(QIcon(self.theme_manager.get_image(self.struct[key][0])))
