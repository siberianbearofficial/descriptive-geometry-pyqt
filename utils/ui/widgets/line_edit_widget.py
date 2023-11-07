from PyQt6.QtWidgets import QLineEdit


class LineEditWidget(QLineEdit):
    def __init__(self, parent=None):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()
        self.setReadOnly(True)

    def mouseDoubleClickEvent(self, a0) -> None:
        self.setReadOnly(False)

    def connect(self, func):
        self.editingFinished.connect(lambda: (self.setReadOnly(True), func()))
