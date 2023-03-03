from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLayout
from PyQt5.QtCore import Qt
from DrawTool import DrawTool


class DrawBar(QWidget):
    def __init__(self, parent, *names):
        super().__init__(parent)

        self.setGeometry(20, 19, 121, 681)
        self.setStyleSheet("background-color: #EAEAEA;\n"
                           "border-radius: 10px;")

        self.strange_widget = QWidget(self)
        self.strange_widget.setFixedSize(self.geometry().size())

        self.layout = QVBoxLayout(self.strange_widget)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(10)

        self.tools = list()

        for name in names:
            draw_tool = DrawTool(name)
            self.tools.append(draw_tool)
            self.layout.addWidget(draw_tool)

    def set_images(self, *images):
        pass

    def set_on_click_listeners(self, *funcs):
        for i in range(len(funcs)):
            self.tools[i].set_on_click_listener(funcs[i])
