from PyQt5 import QtWidgets, QtGui
from utils.drawing.general_object import GeneralObject


ONLY_POSITIVE_ATTRIBUTES = ['radius', 'radius1', 'radius2', 'tube_radius']


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, obj):
        super().__init__()
        self.setFixedSize(300, 400)

        self.obj = obj
        self.dict = obj.to_dict()
        self.save_changes = True
        self.setWindowTitle(self.obj.ag_object.__class__.__name__)

        self.attributes_panel_widget = QtWidgets.QWidget(self)
        self.attributes_panel_widget.setGeometry(10, 10, 265, 330)

        self.attributes_panel = QtWidgets.QWidget(self.attributes_panel_widget)
        self.attributes_panel.setGeometry(10, 10, 265, 100000)

        self.button1 = QtWidgets.QPushButton('Отмена', self)
        self.button1.setGeometry(10, 350, 120, 40)
        self.button1.clicked.connect(lambda *args: self.exit(False))
        self.button2 = QtWidgets.QPushButton('ОК', self)
        self.button2.setGeometry(140, 350, 120, 40)
        self.button2.clicked.connect(lambda *args: self.exit(True))

        label = QtWidgets.QLabel('Name:', self.attributes_panel)
        label.setGeometry(0, 0, 75, 25)
        name_line = QtWidgets.QLineEdit(self.dict['name'], self.attributes_panel)
        name_line.setGeometry(75, 0, 190, 25)
        name_line.textChanged.connect(self.set_name)

        label = QtWidgets.QLabel('Color:', self.attributes_panel)
        label.setGeometry(0, 30, 75, 25)

        self.color_dialog = QtWidgets.QColorDialog()
        self.color_button = QtWidgets.QPushButton(self.attributes_panel)
        self.color_button.setGeometry(75, 30, 100, 25)
        self.color_button.clicked.connect(lambda *args: self.set_color())
        self.color_button.setStyleSheet(f'background: rgb{str(obj.color)}')

        attributes_window = AttributeWindow(self.attributes_panel, self.dict['ag_object'])
        attributes_window.setGeometry(0, 60, 275, attributes_window.h)
        h = attributes_window.h + 70

        if h > 330:
            self.scroll_bar = QtWidgets.QScrollBar(self)
            self.scroll_bar.valueChanged.connect(lambda *args: self.scroll_attributes_panel())
            self.scroll_bar.setGeometry(285, 0, 15, 400)
            self.scroll_bar.setMaximum((h - 330) // 10)

    def scroll_attributes_panel(self):
        self.attributes_panel.move(10, 10 - self.scroll_bar.value() * 10)

    def set_color(self):
        QtWidgets.QColorDialog.setStandardColor(0, QtGui.QColor(*self.obj.color))
        color = self.color_dialog.getColor()
        self.dict['color'] = color.red(), color.green(), color.blue()
        self.color_button.setStyleSheet(f'background: rgb{str((color.red(), color.green(), color.blue()))}')

    def set_name(self, name):
        self.dict['name'] = name

    def exit(self, save_changes):
        self.save_changes = save_changes
        self.close()


class AttributeWindow(QtWidgets.QWidget):
    def __init__(self, parent, dct):
        super().__init__(parent)
        self.h = 0
        y = 0
        for key, item in dct.items():
            attributes_window = AttributeWindow2(self, key, item, dct)
            attributes_window.setGeometry(0, y, 275, attributes_window.h)
            y += attributes_window.h
        self.h = y


class AttributeWindow2(QtWidgets.QWidget):
    def __init__(self, parent, key, item, dct, index=None):
        def set_value(dct, key, value):
            dct[key] = value

        super().__init__(parent)
        y = 0
        self.h = 0
        if isinstance(item, float) or isinstance(item, int):
            label = QtWidgets.QLabel(f'{key}:' if index is None else f'{key}[{index}]:', self)
            label.setGeometry(0, y, 50, 25)
            spin_box = QtWidgets.QDoubleSpinBox(self)
            spin_box.setMaximum(1e100)
            spin_box.setMinimum(0 if key in ONLY_POSITIVE_ATTRIBUTES else -1e100)
            spin_box.setDecimals(4)
            spin_box.setValue(item)
            spin_box.setGeometry(50, y, 150, 25)
            spin_box.valueChanged.connect(lambda value: set_value(dct, key, value))
            y += 30
        if isinstance(item, tuple) and key != 'color' or isinstance(item, list):
            for i in range(len(item)):
                attributes_window = AttributeWindow2(self, key, item[i], dct, index=i)
                attributes_window.setGeometry(0, y, 275, attributes_window.h)
                y += attributes_window.h
        elif isinstance(item, dict):
            label = QtWidgets.QLabel(f'{key}:' if index is None else f'{key}[{index}]:', self)
            label.setGeometry(0, y, 50, 25)
            y += 30
            for key2, item2 in item.items():
                attributes_window = AttributeWindow2(self, key2, item2, dct[key] if index is None else dct[key][index])
                attributes_window.setGeometry(25, y, 275, attributes_window.h)
                y += attributes_window.h
        self.h = y


def open_attribute_window(obj):
    app = QtWidgets.QApplication([])
    window = MainWindow(obj)
    window.show()

    app.exec_()
    if window.save_changes:
        try:
            return GeneralObject.from_dict(obj.plot, window.dict)
        except Exception:
            return obj
    return obj
