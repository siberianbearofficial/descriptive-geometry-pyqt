from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from widget import Widget


class ToolBar(Widget):
    def __init__(self, parent, *names):
        super().__init__(parent)

        self.tools = list()

        # Font
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)

        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px;")

        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)

        for name in names:
            tool = Tool(name, self.central_widget)
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


class Tool(Widget):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.clicked = None
        self.name = name

        # Font
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)

        self.layout = QHBoxLayout(self.central_widget)
        # self.layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(5)

        self.icon = QLabel(self.central_widget)
        self.icon.setMaximumSize(30, 30)
        self.icon.setText('')
        self.icon.setScaledContents(True)
        self.layout.addWidget(self.icon)

        self.label = QLabel(self.central_widget)
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
