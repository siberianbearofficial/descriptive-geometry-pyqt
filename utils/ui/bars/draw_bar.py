from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from utils.ui.bars.draw_tool import DrawTool, DrawToolGroup
from utils.ui.widgets.widget import Widget
from utils.color import *


class DrawBar(Widget):
    def __init__(self, struct, parent, font_manager, theme_manager):
        super().__init__(parent)

        self.theme_manager = theme_manager

        self.setMouseTracking(True)

        self.setStyleSheet(f"background-color: {LIGHT_COLOR};\n"
                           "border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(10)

        self.groups = list()

        for group in struct:
            draw_tool_group = DrawToolGroup(group, struct[group], font_manager)
            self.groups.append(draw_tool_group)
            self.layout.addWidget(draw_tool_group)

    def set_images(self, *images):
        pass

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QMouseEvent):
            DrawToolGroup.group_hovered(None)
            DrawTool.tool_hovered(None)
        return False

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.get_style_sheet(self.__class__.__name__))
