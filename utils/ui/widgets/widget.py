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

        self.filter = self.central_widget.installEventFilter(self)

    def setMouseTracking(self, enable: bool) -> None:
        self.central_widget.setMouseTracking(enable)

    def eventFilter(self, a0, a1) -> bool:
        return super().eventFilter(a0, a1)

    def setStyleSheet(self, stylesheet: str) -> None:
        self.central_widget.setStyleSheet(stylesheet)

    def setMinimumHeight(self, minh: int) -> None:
        super().setMinimumHeight(minh)
        self.central_widget.setMinimumHeight(minh)

    def setMaximumHeight(self, maxh: int) -> None:
        super().setMaximumHeight(maxh)
        self.central_widget.setMaximumHeight(maxh)

    def setFixedHeight(self, fixh: int) -> None:
        super().setFixedHeight(fixh)
        self.central_widget.setFixedHeight(fixh)

    def setFixedWidth(self, fixw: int) -> None:
        super().setFixedWidth(fixw)
        self.central_widget.setFixedWidth(fixw)

    def setMinimumSize(self, minw: int, minh: int) -> None:
        self.setMinimumWidth(minw)
        self.setMinimumHeight(minh)

    def setMaximumSize(self, maxw: int, maxh: int) -> None:
        self.setMaximumWidth(maxw)
        self.setMaximumHeight(maxh)

    def setFixedSize(self, fixw: int, fixh: int) -> None:
        self.setFixedWidth(fixw)
        self.setFixedHeight(fixh)
