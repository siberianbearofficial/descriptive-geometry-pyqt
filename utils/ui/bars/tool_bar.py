from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from utils.ui.bars.tool import Tool


class ToolBar(QWidget):
    def __init__(self, struct, font_manager, theme_manager):
        super().__init__()

        self.tools = list()
        self.theme_manager = theme_manager

        self.setMouseTracking(True)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        for name in struct:
            tool = Tool(name, font_manager).set_on_click_listener(struct[name][0]).set_image(
                struct[name][1])
            self.tools.append(tool)
            layout.addWidget(tool)

    def set_images(self, *tool_images):
        for i in range(len(tool_images)):
            self.tools[i].set_image(tool_images[i])
        return self

    def set_on_click_listeners(self, *funcs):
        for i in range(len(funcs)):
            self.tools[i].set_on_click_listener(funcs[i])
        return self

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QMouseEvent):
            Tool.tool_hovered(None)
        return False

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.bg_style_sheet)
