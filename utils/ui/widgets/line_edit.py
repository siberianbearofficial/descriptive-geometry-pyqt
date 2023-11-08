from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    def __init__(self, tm, text=''):
        super().__init__()
        self.tm = tm
        self.setText(text)
        self.setReadOnly(True)
        self.editingFinished.connect(self._on_editing_finished)

    def mouseDoubleClickEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.setReadOnly(False)
            self.set_styles()
        else:
            super().mouseDoubleClickEvent(a0)

    def _on_editing_finished(self):
        self.setReadOnly(True)
        self.set_styles()

    def set_styles(self):
        if self.isReadOnly():
            self.tm.auto_css(self, palette='Menu', border=False)
        else:
            self.tm.auto_css(self, palette='Main')
