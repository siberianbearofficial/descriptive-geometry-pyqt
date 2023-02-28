from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QFont


class DrawTool(QWidget):
    def __init__(self, name):
        super().__init__()

        self.clicked = None
        self.name = name

        # LAYOUT
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.icon = QLabel(self)
        self.icon.setMaximumSize(QSize(30, 30))
        self.icon.setStyleSheet("border: 2px solid #00ABB3;\n"
                           "border-radius: 10px;\n"
                           "background-color: #ffffff;")
        self.icon.setText("")
        self.icon.setPixmap(QPixmap(":/img/img/point.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setWordWrap(False)
        self.layout.addWidget(self.icon)

        self.label = QLabel(self)
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setText(name)
        self.label.setStyleSheet("color: #00ABB3;")

        self.layout.addWidget(self.label)

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1:
            print('Button pressed!')
            if self.clicked:
                self.clicked(self.name.lower())

    def setText(self, text):
        self.label.setText(text)

    def set_on_click_listener(self, func):
        self.clicked = func
        return self
