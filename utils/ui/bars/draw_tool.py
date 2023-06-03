from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QHoverEvent, QEnterEvent, QMouseEvent

from utils.ui.widgets.label import Label
from utils.ui.widgets.widget import Widget
from utils.color import *


class DrawToolGroup(QWidget):
    hovered_group = None
    HEIGHT_ANIMATION_DURATION = 100
    HEIGHT = 30
    HOVER_HEIGHT = 80
    SPACING = 10

    groupHeightChanged = pyqtSignal(int)

    def __init__(self, name, struct, font_manager):
        super().__init__()

        # LAYOUT
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(DrawToolGroup.SPACING)
        self.layout.setAlignment(Qt.AlignTop)

        self._group_height = DrawToolGroup.HEIGHT
        self.setFixedHeight(DrawToolGroup.HEIGHT)
        self.groupHeightChanged.connect(self.group_height_changed)

        self.height_anim = QPropertyAnimation(self, b"group_height")
        self.height_anim.setDuration(DrawTool.COLOR_ANIMATION_DURATION)
        self.height_anim.finished.connect(self.height_anim_finished)

        self.tools = list()
        for tool_name in struct:
            # print(tool_name, struct[tool_name])
            tool = DrawTool(tool_name, font_manager).set_on_click_listener(struct[tool_name][0])
            self.tools.append(tool)
            self.layout.addWidget(tool)
        self.hide_tools()
        self.tools_hidden = True

        self.hover_height = DrawToolGroup.HEIGHT * len(self.tools) + (len(self.tools) - 1) * DrawToolGroup.SPACING

        self.filter = self.installEventFilter(self)

    def height_anim_finished(self):
        self.hide_tools() if self.tools_hidden else self.show_tools()

    @pyqtProperty(int)
    def group_height(self):
        return self._group_height

    @group_height.setter
    def group_height(self, height):
        if self._group_height != height:
            self._group_height = height
            self.groupHeightChanged.emit(height)

    def group_height_changed(self, height):
        self.setFixedHeight(height)

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QEnterEvent):
            DrawToolGroup.group_hovered(self)
        elif isinstance(a1, QMouseEvent):
            DrawTool.tool_hovered(None)
        return False

    def hover(self):
        # self.show_tools()
        self.tools_hidden = False
        self.height_anim.setEndValue(self.hover_height)
        self.height_anim.start()

    def unhover(self):
        self.hide_tools()
        self.tools_hidden = True
        self.height_anim.setEndValue(DrawToolGroup.HEIGHT)
        self.height_anim.start()

    def show_tools(self):
        for i in range(1, len(self.tools)):
            self.tools[i].show()

    def hide_tools(self):
        for i in range(1, len(self.tools)):
            self.tools[i].hide()

    @staticmethod
    def group_hovered(group):
        if DrawToolGroup.hovered_group and DrawToolGroup.hovered_group != group:
            DrawToolGroup.hovered_group.unhover()
        if DrawToolGroup.hovered_group != group and group:
            group.hover()
        DrawToolGroup.hovered_group = group


class DrawTool(QWidget):
    hovered_tool = None
    COLOR_ANIMATION_DURATION = 100
    COLOR = ACCENT_COLOR
    HOVER_COLOR = DARK_COLOR
    ICON_SIZE = 30

    def __init__(self, name, font_manager):
        super().__init__()

        self.clicked = None
        self.name = name

        # LAYOUT
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        # ICON
        self.icon = QLabel()
        self.icon.setMaximumSize(DrawTool.ICON_SIZE, DrawTool.ICON_SIZE)
        self.icon.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};\n"
                                "border-radius: 10px;\n"
                                f"background-color: {WHITE_COLOR};")
        self.icon.setPixmap(QPixmap(":/img/img/point.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setWordWrap(False)
        self.layout.addWidget(self.icon)

        self.label = Label()
        self.label.setColor(DrawTool.COLOR)
        self.label.setFont(font_manager.bold())
        self.label.setText(name)

        self.color_anim = QPropertyAnimation(self.label, b"color")
        self.color_anim.setDuration(DrawTool.COLOR_ANIMATION_DURATION)

        self.layout.addWidget(self.label)

        self.filter = self.installEventFilter(self)

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
