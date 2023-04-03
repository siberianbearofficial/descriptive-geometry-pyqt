from PyQt5.QtWidgets import QVBoxLayout
from utils.ui.bars.tool import Tool
from utils.ui.widgets.widget import Widget
from utils.color import *


class ToolBar(Widget):
    def __init__(self, struct, parent, font_manager):
        super().__init__(parent)

        self.tools = list()

        self.setStyleSheet(f"background-color: {LIGHT_COLOR}; border-radius: 10px;")

        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        for name in struct:
            tool = Tool(name, font_manager, self.central_widget).set_on_click_listener(struct[name][0]).set_image(
                struct[name][1])
            self.tools.append(tool)
            self.layout.addWidget(tool)

    def set_images(self, *tool_images):
        for i in range(len(tool_images)):
            self.tools[i].set_image(tool_images[i])
        return self

    def set_on_click_listeners(self, *funcs):
        for i in range(len(funcs)):
            self.tools[i].set_on_click_listener(funcs[i])
        return self
