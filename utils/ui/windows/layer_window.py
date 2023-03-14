from PyQt5.QtWidgets import QWidget, QMainWindow, QMenuBar, QLineEdit, QLabel, QCheckBox, QVBoxLayout, QScrollArea, QAction
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt


class LayerWindow(QMainWindow):
    addLayer = pyqtSignal()
    removeLayer = pyqtSignal(int)
    selectLayer = pyqtSignal(int)
    renameLayer = pyqtSignal(str)
    setLayerColor = pyqtSignal(int, tuple)
    setLayerHidden = pyqtSignal(int, bool)
    setLayerLineStyle = pyqtSignal(int, int)

    def __init__(self, layers, current_layer):
        super(LayerWindow, self).__init__()
        self.setFixedSize(640, 480)
        self.setWindowTitle('DescriptiveGeometry - Layers')

        self.menu_bar = QMenuBar()
        self.menu_bar.addAction('New layer')
        self.menu_bar.actions()[0].triggered.connect(lambda *args: self.addLayer.emit())
        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.menu_bar.setFont(font)
        self.menu_bar.setStyleSheet("color: #00ABB3;")

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 30, 640, 450)
        self.scroll_area.setStyleSheet("background-color: #3C4048;")

        self.layers_widget = QWidget(self)
        self.layers_widget.setGeometry(0, 0, 620, 5)
        self.layers_widget.setStyleSheet("background-color: #3C4048;")
        self.layout = QVBoxLayout(self.layers_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(5)

        self.layer_bars = []
        self.update_layer_list(layers, current_layer)

        self.select_layer(current_layer)

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
            widget = LayerBar(self, i, name=layers[i].name, color=layers[i].color, hidden=layers[i].hidden)
            self.layer_bars.append(widget)
            self.layout.addWidget(widget)
            widget.select.connect(lambda index: self.select_layer(index))
            widget.show_hide.connect(lambda ind, flag: self.setLayerHidden.emit(ind, flag))
            widget.delete.connect(self.delete_layer)

        self.layers_widget.setFixedSize(620, 5 + len(self.layer_bars) * 45)
        self.select_layer(current_layer)

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
        self.removeLayer.emit(index)
        self.layers_widget.setFixedSize(620, 5 + len(self.layer_bars) * 45)

    def select_layer(self, index):
        self.selectLayer.emit(index)
        for layer in self.layer_bars:
            layer.selection_bar.setChecked(False)
        self.layer_bars[index].selection_bar.setChecked(True)


class LayerBar(QWidget):
    select = pyqtSignal(int)
    rename = pyqtSignal(str)
    show_hide = pyqtSignal(int, bool)
    delete = pyqtSignal(int)

    def __init__(self, parent, index, **kwargs):
        super(LayerBar, self).__init__(parent)
        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px")
        self.index = index

        self.strange_widget = QWidget(self)
        self.strange_widget.setFixedSize(600, 40)

        self.selection_bar = QCheckBox(self)
        self.selection_bar.setGeometry(5, 5, 20, 30)
        self.selection_bar.clicked.connect(
            lambda flag: self.select.emit(self.index) if flag else self.selection_bar.setChecked(True))

        self.name_bar = QLineEdit(self.strange_widget)
        self.name_bar.setText(kwargs.get('name', ''))
        self.name_bar.setStyleSheet("color: #00ABB3;\n"
                                    "background-color: #EAEAEA;\n"
                                    "border: 2px solid #00ABB3;\n"
                                    "padding-left: 3px;")
        self.name_bar.setGeometry(25, 5, 230, 30)
        self.name_bar.editingFinished.connect(lambda: self.rename.emit(self.name_bar.text()))

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

        self.button_delete = Button(self, 'D')
        self.button_delete.move(330, 5)
        self.button_delete.clicked.connect(lambda: self.delete.emit(self.index))

    def show_hide_func(self, flag):
        self.show_hide.emit(self.index, flag)
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
        self.setStyleSheet("border: 2px solid #00ABB3;\n"
                           "border-radius: 10px;\n"
                           "background-color: #ffffff;")
        self.icon = QLabel(self)
        self.icon.setFixedSize(self.size())
        if pixmap:
            self.icon.setPixmap(QPixmap(pixmap))
        if text:
            self.icon.setText(text)
        if color:
            self.setStyleSheet(f"background-color: rgb{str(color)};")

    def mousePressEvent(self, a0):
        if a0.button() == 1:
            self.clicked.emit()
