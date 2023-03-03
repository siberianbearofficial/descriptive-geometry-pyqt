from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


class ToolBar(QWidget):
    def __init__(self, parent, *names):
        super().__init__(parent)

        self.tools = list()

        # Font
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)

        self.setGeometry(890, 19, 171, 111)
        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px;")

        self.strange_widget = QWidget(self)
        self.strange_widget.setGeometry(0, 0, 171, 111)

        # Layout
        self.tool_bar_layout = QVBoxLayout(self.strange_widget)
        self.tool_bar_layout.setContentsMargins(15, 8, 15, 8)
        self.tool_bar_layout.setSpacing(0)

        for name in names:
            tool = Tool(name, self.strange_widget)
            self.tools.append(tool)
            self.tool_bar_layout.addWidget(tool)

        # self.tool_bar_tool_2 = QWidget(self.verticalLayoutWidget_5)
        # self.widget2 = QWidget(self.tool_bar_tool_2)
        # self.widget2.setGeometry(0, 0, 141, 32)
        # self.tool_bar_tool_2_layout = QHBoxLayout(self.widget2)
        # self.tool_bar_tool_2_layout.setSizeConstraint(QLayout.SetMinimumSize)
        # self.tool_bar_tool_2_layout.setContentsMargins(0, 0, 0, 0)
        # self.tool_bar_tool_2_layout.setSpacing(5)
        # self.tool_bar_tool_2_icon = QLabel(self.widget2)
        # self.tool_bar_tool_2_icon.setMaximumSize(30, 30)
        # self.tool_bar_tool_2_icon.setText("")
        # self.tool_bar_tool_2_icon.setPixmap(QPixmap(":/img/img/angle_icon.png"))
        # self.tool_bar_tool_2_icon.setScaledContents(True)
        # self.tool_bar_tool_2_layout.addWidget(self.tool_bar_tool_2_icon)
        # self.tool_bar_tool_2_label = QLabel(self.widget2)
        # self.tool_bar_tool_2_label.setMaximumSize(16777215, 50)
        # self.tool_bar_tool_2_label.setFont(font)
        # self.tool_bar_tool_2_label.setStyleSheet("color: #00ABB3;")
        # self.tool_bar_tool_2_layout.addWidget(self.tool_bar_tool_2_label)
        # self.tool_bar_layout.addWidget(self.tool_bar_tool_2)
        # self.tool_bar_tool_1 = QWidget(self.verticalLayoutWidget_5)
        # self.widget3 = QWidget(self.tool_bar_tool_1)
        # self.widget3.setGeometry(0, 0, 141, 32)
        # self.tool_bar_tool_1_layout = QHBoxLayout(self.widget3)
        # self.tool_bar_tool_1_layout.setSizeConstraint(QLayout.SetMinimumSize)
        # self.tool_bar_tool_1_layout.setContentsMargins(0, 0, 0, 0)
        # self.tool_bar_tool_1_layout.setSpacing(5)
        # self.tool_bar_tool_1_icon = QLabel(self.widget3)
        # self.tool_bar_tool_1_icon.setEnabled(True)
        # self.tool_bar_tool_1_icon.setMaximumSize(30, 30)
        # self.tool_bar_tool_1_icon.setText("")
        # self.tool_bar_tool_1_icon.setPixmap(QPixmap(":/img/img/ruler_icon.png"))
        # self.tool_bar_tool_1_icon.setScaledContents(True)
        # self.tool_bar_tool_1_layout.addWidget(self.tool_bar_tool_1_icon)
        # self.tool_bar_tool_1_label = QLabel(self.widget3)
        # self.tool_bar_tool_1_label.setMaximumSize(16777215, 50)
        # self.tool_bar_tool_1_label.setFont(font)
        # self.tool_bar_tool_1_label.setStyleSheet("color: #00ABB3;")
        # self.tool_bar_tool_1_layout.addWidget(self.tool_bar_tool_1_label)
        # self.tool_bar_layout.addWidget(self.tool_bar_tool_1)

    def set_images(self, *tool_images):
        for i in range(len(tool_images)):
            self.tools[i].set_image(tool_images[i])
        return self

    def set_on_click_listeners(self, *funcs):
        for i in range(len(funcs)):
            self.tools[i].set_on_click_listener(funcs[i])


class Tool(QWidget):
    def __init__(self, name, parent=None):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        self.clicked = None
        self.name = name

        # Font
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)

        self.strange_widget = QWidget(self)
        self.strange_widget.setGeometry(0, 0, 141, 32)

        self.layout = QHBoxLayout(self.strange_widget)
        self.layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.icon = QLabel(self.strange_widget)
        self.icon.setMaximumSize(30, 30)
        self.icon.setText('')
        self.icon.setScaledContents(True)
        self.layout.addWidget(self.icon)

        self.label = QLabel(self.strange_widget)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #00ABB3;")
        self.label.setText(name)
        self.layout.addWidget(self.label)

    def set_image(self, image):
        self.icon.setPixmap(QPixmap(f":/img/img/{image}"))
        return self

    def set_on_click_listener(self, func):
        self.clicked = func
        return self

    def mousePressEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton and self.clicked:
            print('Click on tool:', self.name)
            self.clicked()
