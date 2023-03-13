from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from widget import Widget

from random import randint


class InspectorBarObject(Widget):
    def __init__(self, parent):
        super().__init__(parent)

        # self.setStyleSheet('background-color: #ff0000;')

        # Font
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)

        # Layout
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Icon
        self.icon = QLabel(self.central_widget)
        self.icon.setFixedSize(20, 20)
        self.icon.setText("")
        self.icon.setPixmap(QPixmap(":/img/img/inspector_bar_object_icon.png"))
        self.icon.setScaledContents(True)
        self.layout.addWidget(self.icon)

        # Label
        self.label = QLabel(self.central_widget)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #00ABB3;")
        self.label.setText(f'A: Cylinder {randint(100,200)}')
        self.layout.addWidget(self.label)
