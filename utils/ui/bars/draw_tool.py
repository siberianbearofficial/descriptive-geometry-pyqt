from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QHoverEvent, QEnterEvent

from utils.ui.widgets.label import Label
from utils.ui.widgets.widget import Widget
from utils.color import *


class DrawTool(Widget):
    hovered_tool = None
    COLOR_ANIMATION_DURATION = 100
    COLOR = ACCENT_COLOR
    HOVER_COLOR = DARK_COLOR
    ICON_SIZE = 30

    def __init__(self, name, parent, font_manager):
        super().__init__(parent)

        self.clicked = None
        self.name = name

        # LAYOUT
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.icon = QLabel(self.central_widget)
        self.icon.setMaximumSize(DrawTool.ICON_SIZE, DrawTool.ICON_SIZE)
        self.icon.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};\n"
                                "border-radius: 10px;\n"
                                f"background-color: {WHITE_COLOR};")
        self.icon.setPixmap(QPixmap(":/img/img/point.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setWordWrap(False)
        self.layout.addWidget(self.icon)

        self.label = Label(self.central_widget)
        self.label.setColor(DrawTool.COLOR)

        self.label.setFont(font_manager.bold())
        self.label.setText(name)

        self.color_anim = QPropertyAnimation(self.label, b"color")
        self.color_anim.setDuration(DrawTool.COLOR_ANIMATION_DURATION)

        self.layout.addWidget(self.label)

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1:
            if self.clicked:
                self.clicked()

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QEnterEvent):
            DrawTool.tool_hovered(self)
        return False

    def set_text(self, text):
        self.label.setText(text)

    def set_on_click_listener(self, func):
        self.clicked = func
        return self

    def hover(self):
        self.color_anim.setEndValue(QColor(DrawTool.HOVER_COLOR))
        self.color_anim.start()

    def unhover(self):
        self.color_anim.setEndValue(QColor(DrawTool.COLOR))
        self.color_anim.start()

    @staticmethod
    def tool_hovered(tool):
        if DrawTool.hovered_tool and DrawTool.hovered_tool != tool:
            DrawTool.hovered_tool.unhover()
        if DrawTool.hovered_tool != tool and tool:
            tool.hover()
        DrawTool.hovered_tool = tool
