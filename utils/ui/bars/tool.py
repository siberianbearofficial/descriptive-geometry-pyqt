from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QEnterEvent

from utils.ui.widgets.label import Label
from utils.ui.widgets.widget import Widget
from utils.color import *


class Tool(Widget):
    hovered_tool = None
    COLOR_ANIMATION_DURATION = 100
    COLOR = ACCENT_COLOR
    HOVER_COLOR = DARK_COLOR
    ICON_SIZE = 30

    def __init__(self, name, font_manager, parent=None):
        super().__init__(parent)

        self.clicked = None
        self.name = name

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.icon = QLabel(self.central_widget)
        self.icon.setMaximumSize(Tool.ICON_SIZE, Tool.ICON_SIZE)
        self.icon.setText('')
        self.icon.setScaledContents(True)
        self.layout.addWidget(self.icon)

        self.label = Label(self.central_widget)
        self.label.setFont(font_manager.bold())
        self.label.setText(name)
        self.label.setColor(Tool.COLOR)

        self.color_anim = QPropertyAnimation(self.label, b"color")
        self.color_anim.setDuration(Tool.COLOR_ANIMATION_DURATION)

        self.layout.addWidget(self.label)

    def set_image(self, image):
        self.icon.setPixmap(QPixmap(f":/img/img/{image}"))
        return self

    def set_on_click_listener(self, func):
        self.clicked = func
        return self

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QEnterEvent):
            Tool.tool_hovered(self)
        return False

    def mousePressEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton and self.clicked:
            self.clicked()

    def hover(self):
        self.color_anim.setEndValue(QColor(Tool.HOVER_COLOR))
        self.color_anim.start()

    def unhover(self):
        self.color_anim.setEndValue(QColor(Tool.COLOR))
        self.color_anim.start()

    @staticmethod
    def tool_hovered(tool):
        if Tool.hovered_tool and Tool.hovered_tool != tool:
            Tool.hovered_tool.unhover()
        if Tool.hovered_tool != tool and tool:
            tool.hover()
        Tool.hovered_tool = tool
