from PyQt5.QtWidgets import QWidget, QMainWindow, QMenuBar, QLineEdit, QLabel, QCheckBox, QVBoxLayout, QScrollArea, \
    QColorDialog, QComboBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt

from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *


class LayerWindow(QMainWindow):
    def __init__(self, func_add_layer, func_delete_layer, func_select_layer, func_rename_layer, func_layer_hidden,
                 func_layer_color, func_layer_thickness):
        super(LayerWindow, self).__init__()
        self.setFixedSize(640, 480)
        self.setWindowTitle('DescriptiveGeometry - Layers')
        self.func_add_layer = func_add_layer
        self.func_delete_layer = func_delete_layer
        self.func_select_layer = func_select_layer
        self.func_rename_layer = func_rename_layer
        self.func_layer_hidden = func_layer_hidden
        self.func_layer_color = func_layer_color
        self.func_layer_thickness = func_layer_thickness

        self.menu_bar = QMenuBar()
        self.menu_bar.addAction('New layer')
        self.menu_bar.actions()[0].triggered.connect(lambda *args: self.func_add_layer())
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.menu_bar.setFont(font)
        self.menu_bar.setStyleSheet(f"color: {ACCENT_COLOR};")

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 30, 640, 450)    # TODO: REMOVE!
        self.scroll_area.setStyleSheet(f"background-color: {DARK_COLOR};")

        self.layers_widget = QWidget(self)
        self.layers_widget.setGeometry(0, 0, 620, 5)
        self.layers_widget.setStyleSheet(f"background-color: {DARK_COLOR};")
        self.layout = QVBoxLayout(self.layers_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(5)

        self.layer_bars = []

        self.setMenuBar(self.menu_bar)
        self.scroll_area.setWidget(self.layers_widget)

    def update_layer_list(self, layers, current_layer):
        for layer in self.layer_bars:
            self.layout.removeWidget(layer)
            layer.hide()
            layer.destroy()
        self.layers_widget.setFixedSize(620, 5)
        self.layer_bars = []
        for i in range(len(layers)):
            widget = LayerBar(
                self, i, self.func_select_layer, self.func_rename_layer, self.func_layer_hidden, self.func_delete_layer,
                self.func_layer_color, self.func_layer_thickness,
                name=layers[i].name, color=layers[i].color, hidden=layers[i].hidden, thickness=layers[i].thickness)
            self.layer_bars.append(widget)
            self.layout.addWidget(widget)

        self.layers_widget.setFixedSize(620, 5 + len(self.layer_bars) * 45)
        self.select_layer(current_layer)

    def add_layer(self, layer, index=None):
        if index is not None:
            i = index
        else:
            i = len(self.layer_bars)
        widget = LayerBar(
            self, i, self.func_select_layer, self.func_rename_layer, self.func_layer_hidden, self.func_delete_layer,
            self.func_layer_color, self.func_layer_thickness,
            name=layer.name, color=layer.color, hidden=layer.hidden, thickness=layer.thickness)
        self.layer_bars.insert(i, widget)
        self.layout.insertWidget(i, widget)
        self.layers_widget.setFixedSize(620, 5 + len(self.layer_bars) * 45)

    def delete_layer(self, index):
        if len(self.layer_bars) <= 1:
            return
        flag = self.layer_bars[index].selection_bar.isChecked()
        if flag:
            return
        self.layer_bars[index].hide()
        self.layer_bars[index].destroy()

        self.layout.removeWidget(self.layer_bars[index])
        self.layer_bars.pop(index)
        for i in range(len(self.layer_bars)):
            self.layer_bars[i].index = i
        self.layers_widget.setFixedSize(620, 5 + len(self.layer_bars) * 45)

    def hide_layer(self, index, hidden):
        if hidden:
            self.layer_bars[index].button_show.show()
            self.layer_bars[index].button_hide.hide()
        else:
            self.layer_bars[index].button_show.hide()
            self.layer_bars[index].button_hide.show()

    def rename_layer(self, index, name):
        self.layer_bars[index].name_bar.setText(name)

    def select_layer(self, index):
        for layer in self.layer_bars:
            layer.selection_bar.setChecked(False)
        self.layer_bars[index].selection_bar.setChecked(True)

    def set_layer_color(self, index, color):
        self.layer_bars[index].button_color.set_color(color)

    def set_layer_thickness(self, index, thickness):
        self.layer_bars[index].thickness_combobox.setCurrentIndex(thickness)


class LayerBar(QWidget):
    def __init__(self, parent, index, func_select, func_rename, func_hide, func_delete, func_color, func_thickness,
                 **kwargs):
        super(LayerBar, self).__init__(parent)
        self.setStyleSheet(f"background-color: {LIGHT_COLOR}; border-radius: 10px")
        self.index = index
        self.func_select = func_select
        self.func_rename = func_rename
        self.func_hide = func_hide
        self.func_delete = func_delete
        self.func_color = func_color
        self.func_thickness = func_thickness

        self.strange_widget = QWidget(self)
        self.strange_widget.setFixedSize(600, 40)

        self.selection_bar = QCheckBox(self)
        self.selection_bar.setGeometry(5, 5, 20, 30)
        self.selection_bar.clicked.connect(
            lambda flag: self.func_select(self.index) if flag else self.selection_bar.setChecked(True))

        self.name_bar = LineEditWidget(self.strange_widget)
        self.name_bar.setText(kwargs.get('name', ''))
        self.name_bar.setStyleSheet(f"color: {ACCENT_COLOR};"
                                    f"background-color: {LIGHT_COLOR};"
                                    f"border: 2px solid {ACCENT_COLOR};"
                                    "padding-left: 3px;")
        self.name_bar.setGeometry(25, 5, 230, 30)
        self.name_bar.connect(lambda: self.func_rename(self.name_bar.text(), self.index))

        self.button_show = Button(self, 'S')
        self.button_show.move(260, 5)
        self.button_show.clicked.connect(lambda: self.show_hide_func(False))

        self.button_hide = Button(self, 'H')
        self.button_hide.move(260, 5)
        self.button_hide.clicked.connect(lambda: self.show_hide_func(True))
        if kwargs.get('hidden'):
            self.button_hide.hide()
        else:
            self.button_show.hide()

        self.button_color = Button(self, color=kwargs.get('color', None))
        self.button_color.move(295, 5)
        self.button_color.clicked.connect(lambda: self.func_color(Color(QColorDialog.getColor()), self.index))

        self.thickness_combobox = QComboBox(self)
        self.thickness_combobox.setGeometry(330, 5, 70, 30)
        # self.thickness_combobox.setFont(font_manager.bold())
        self.thickness_combobox.setStyleSheet("QComboBox {\n"
                                              f"color: {ACCENT_COLOR};\n"
                                              f"background-color: {LIGHT_COLOR};\n"
                                              f"border: 2px solid {ACCENT_COLOR};\n"
                                              "padding-right: 1px;\n"
                                              "}\n"
                                              "QComboBox::drop-down:button {\n"
                                              "border-radius: 5px;\n"
                                              "}")
        self.thickness_combobox.setMaxVisibleItems(3)
        self.thickness_combobox.addItem("light")
        self.thickness_combobox.addItem("medium")
        self.thickness_combobox.addItem("bold")
        self.thickness_combobox.setCurrentIndex(kwargs.get('thickness', 0))
        self.thickness_combobox.currentIndexChanged.connect(lambda t: self.func_thickness(t, self.index))

        self.button_delete = Button(self, 'D')
        self.button_delete.move(405, 5)
        self.button_delete.clicked.connect(lambda: self.func_delete(self.index))

    def show_hide_func(self, flag):
        self.func_hide(self.index, flag)
        if flag:
            self.button_show.show()
            self.button_hide.hide()
        else:
            self.button_show.hide()
            self.button_hide.show()


class Button(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent, text='', color=None, pixmap=None):
        super(Button, self).__init__(parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};\n"
                           "border-radius: 10px;\n"
                           f"background-color: {WHITE_COLOR};")
        self.icon = QLabel(self)
        self.icon.setFixedSize(self.size())
        if pixmap:
            self.icon.setPixmap(QPixmap(pixmap))
        if text:
            self.icon.setText(text)
        if color:
            self.setStyleSheet(f"background-color: {color};")

    def mousePressEvent(self, a0):
        if a0.button() == 1:
            self.clicked.emit()

    def set_color(self, color):
        if color is not None:
            self.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};\n"
                               "border-radius: 10px;\n"
                               f"background-color: {color};")
        else:
            self.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};\n"
                               "border-radius: 10px;\n"
                               f"background-color: {WHITE_COLOR};")
