from PyQt5.QtWidgets import QWidget, QVBoxLayout


class Widget(QWidget):
    def __init__(self, parent):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.central_widget = QWidget()
        self.central_widget.setMinimumSize(self.geometry().size())

        layout.addWidget(self.central_widget)

    def setStyleSheet(self, stylesheet: str) -> None:
        self.central_widget.setStyleSheet(stylesheet)
