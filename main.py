from PyQt5.QtWidgets import QApplication
from utils.ui.windows.main_window import MainWindow

import sys


def main():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
