from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap
from utils.ui.widgets.widget import Widget


class Tool(Widget):
    def __init__(self, name, font_manager, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QWidget {"
                           "color: #00ABB3;"
                           "}"
                           "QWidget::hover {"
                           "color: #3C4048;"
                           "}")

        self.clicked = None
        self.name = name

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.icon = QLabel(self.central_widget)
        self.icon.setMaximumSize(30, 30)
        self.icon.setText('')
        self.icon.setScaledContents(True)
        self.layout.addWidget(self.icon)

        self.label = QLabel(self.central_widget)
        self.label.setFont(font_manager.bold())
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
            self.clicked()
