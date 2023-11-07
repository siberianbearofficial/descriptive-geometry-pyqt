from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from utils.ui.bars.draw_tool import DrawTool
from utils.ui.widgets.button import Button


class DrawBar(QWidget):
    def __init__(self, struct: dict[str: dict[str: tuple]], theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.struct = struct

        self.setFixedWidth(52)

        self.buttons = dict()

        strange_layout = QVBoxLayout()
        strange_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(strange_layout)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        strange_widget.setLayout(layout)

        for key, item in struct.items():
            if len(item) == 1:
                button = Button(self.theme_manager, tuple(item.values())[0][0], css='Menu', tooltip=tuple(item.keys())[0])
                button.clicked.connect(tuple(item.values())[0][1])
                button.setFixedSize(42, 30)
                self.buttons[key] = button
                layout.addWidget(button)
            else:
                draw_tool = DrawTool(self.theme_manager, item)
                self.buttons[key] = draw_tool
                layout.addWidget(draw_tool)

    def set_styles(self):
        self.setStyleSheet(f"background-color: {self.theme_manager['MenuColor']};"
                           f"border-right: 1px solid {self.theme_manager['BorderColor']}")
        for el in self.buttons.values():
            el.set_styles()
