from PyQt5.QtWidgets import QApplication
from utils.ui.windows.main_window import MainWindow

import sys


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '-t':
        import core.test_angem
        return
    
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
