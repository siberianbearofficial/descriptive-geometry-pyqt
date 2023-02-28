from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

import utils.history.serializer as srl
from test import Ui_MainWindow

import sys


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('DescriptiveGeometry')
        self.setFixedSize(1080, 720)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def keyPressEvent(self, a0) -> None:
        self.ui.plot.keyPressEvent(a0)



def main():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
