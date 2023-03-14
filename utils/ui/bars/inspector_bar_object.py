from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from utils.ui.widgets.widget import Widget

from random import randint


class InspectorBarObject(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

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
        self.label.setFont(font_manager.bold())
        self.label.setStyleSheet("color: #00ABB3;")
        self.label.setText(f'A: Cylinder {randint(100,200)}')
        self.layout.addWidget(self.label)
