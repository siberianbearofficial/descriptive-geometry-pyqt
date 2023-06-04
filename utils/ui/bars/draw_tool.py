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
    BG_COLOR = LIGHT_COLOR
    HOVER_BG_COLOR = WHITE_COLOR

    groupHeightChanged = pyqtSignal(int)
    groupBackgroundColorChanged = pyqtSignal(QColor)

    def __init__(self, name, struct, font_manager):
        super().__init__(None)

        # LAYOUT
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        strange_widget = QWidget()
        layout.addWidget(strange_widget)
        self.layout = QVBoxLayout(strange_widget)
        self.layout.setContentsMargins(DrawToolGroup.SPACING, DrawToolGroup.SPACING,
                                       DrawToolGroup.SPACING, DrawToolGroup.SPACING)
        self.layout.setSpacing(DrawToolGroup.SPACING)
        self.layout.setAlignment(Qt.AlignTop)

        self._group_height = DrawToolGroup.HEIGHT + DrawToolGroup.SPACING * 2
        self.setFixedHeight(self._group_height)
        self.groupHeightChanged.connect(self.group_height_changed)

        self.height_anim = QPropertyAnimation(self, b"group_height")
        self.height_anim.setStartValue(self._group_height)
        self.height_anim.setDuration(DrawToolGroup.HEIGHT_ANIMATION_DURATION)
        self.height_anim.finished.connect(self.height_anim_finished)
        self._height_anim_finished_flag = True

        self._bg_color = DrawToolGroup.BG_COLOR
        self.setStyleSheet(f'border-radius: 10px;'
                           f'background-color: {DrawToolGroup.BG_COLOR};')
        self.groupBackgroundColorChanged.connect(self.group_background_color_changed)

        self.background_color_anim = QPropertyAnimation(self, b"group_background_color")
        self.background_color_anim.setStartValue(QColor(self._bg_color))
        self.background_color_anim.setDuration(DrawToolGroup.HEIGHT_ANIMATION_DURATION)

        self.tools = list()
        for tool_name in struct:
            tool = DrawTool(tool_name, font_manager).set_on_click_listener(struct[tool_name][0])
            self.tools.append(tool)
            self.layout.addWidget(tool)
        self.hide_tools()
        self.tools_hidden = True

        self.hover_height = DrawToolGroup.HEIGHT * len(self.tools) + (len(self.tools) + 1) * DrawToolGroup.SPACING

        self.filter = self.installEventFilter(self)

    def height_anim_finished(self):
        if self.tools_hidden:
            self.show_tools()
            self.tools_hidden = False
        else:
            self.tools_hidden = True
        self._height_anim_finished_flag = True

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

    @pyqtProperty(QColor)
    def group_background_color(self):
        return self._bg_color

    @group_background_color.setter
    def group_background_color(self, color):
        if self._bg_color != color:
            self._bg_color = color
            self.groupBackgroundColorChanged.emit(color)

    def group_background_color_changed(self, color):
        self.setStyleSheet(f'border-radius: 10px;'
                           f'background-color: {Color(color)};')

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QEnterEvent):
            DrawToolGroup.group_hovered(self)
        elif isinstance(a1, QMouseEvent):
            DrawTool.tool_hovered(None)
        return False

    def hover(self):
        if len(self.tools) > 1:
            self.height_anim.setEndValue(self.hover_height)
            self._height_anim_finished_flag = False
            self.height_anim.start()
        self.background_color_anim.setEndValue(QColor(DrawToolGroup.HOVER_BG_COLOR))
        self.background_color_anim.start()

    def unhover(self):
        if not self._height_anim_finished_flag:
            self.tools_hidden = False
        if len(self.tools) > 1:
            self.hide_tools()
            self.height_anim.setEndValue(DrawToolGroup.HEIGHT + DrawToolGroup.SPACING * 2)
            self._height_anim_finished_flag = False
            self.height_anim.start()
        self.background_color_anim.setEndValue(QColor(DrawToolGroup.BG_COLOR))
        self.background_color_anim.start()

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
                                "border-radius: 10px;\n")
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
