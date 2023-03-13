from PyQt5.QtWidgets import QVBoxLayout, QWidget


class Column(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setGeometry(self.geometry())
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)  # TODO: replace it with a specified constant

    def add(self, el, stretch=None):
        if el:
            if stretch:
                self.layout.addWidget(el, stretch)
            else:
                self.layout.addWidget(el)
        return self
