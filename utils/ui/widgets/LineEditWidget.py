from PyQt5.QtWidgets import QLineEdit


class LineEditWidget(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setReadOnly(True)

    def mouseDoubleClickEvent(self, a0) -> None:
        self.setReadOnly(False)

    def connect(self, func):
        self.editingFinished.connect(lambda: (self.setReadOnly(True), func()))
