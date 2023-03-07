from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


class InspectorBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setGeometry(890, 500, 171, 201)
        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px;")

        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)

        self.strange_widget = QWidget(self)
        self.strange_widget.setFixedSize(self.geometry().width(), self.geometry().height())

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)

        for i in range(7):

            # Widget
            inspector_bar_object = QWidget(self)
            inspector_bar_object.setFixedHeight(20)

            # Layout
            inspector_bar_object_layout = QHBoxLayout(inspector_bar_object)
            inspector_bar_object_layout.setContentsMargins(0, 0, 0, 0)
            inspector_bar_object_layout.setSpacing(5)

            # Icon
            inspector_bar_object_icon = QLabel(inspector_bar_object)
            inspector_bar_object_icon.setMaximumSize(20, 20)
            inspector_bar_object_icon.setText("")
            inspector_bar_object_icon.setPixmap(QPixmap(":/img/img/inspector_bar_object_icon.png"))
            inspector_bar_object_icon.setScaledContents(True)
            inspector_bar_object_layout.addWidget(inspector_bar_object_icon)

            # Label
            inspector_bar_object_label = QLabel(inspector_bar_object)
            inspector_bar_object_label.setFont(font)
            inspector_bar_object_label.setStyleSheet("color: #00ABB3;")
            inspector_bar_object_label.setText(f'A: Cylinder {i}')
            inspector_bar_object_layout.addWidget(inspector_bar_object_label)

            self.layout.addWidget(inspector_bar_object)

            self.setLayout(self.layout)
