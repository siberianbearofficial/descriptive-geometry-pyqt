from uuid import UUID

from PyQt6.QtWidgets import QWidget, QMainWindow, QMenuBar, QLineEdit, QLabel, QCheckBox, QVBoxLayout, QScrollArea, \
    QColorDialog, QComboBox, QDialog, QHBoxLayout
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt

from core.config import APP_NAME
from utils.objects.layer import Layer
from utils.ui.widgets.button import Button
from utils.ui.widgets.color_button import ColorButton
from utils.ui.widgets.line_edit import LineEdit
from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *


class LayerWindow(QDialog):
    def __init__(self, theme_manager, object_manager):
        super(LayerWindow, self).__init__()
        self.tm = theme_manager
        self.object_manager = object_manager
        self.items = dict()

        self.resize(640, 480)
        self.setWindowTitle(f'{APP_NAME} - Layers')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self._top_widget = QWidget()
        main_layout.addWidget(self._top_widget)
        strange_layout = QHBoxLayout()
        self._top_widget.setLayout(strange_layout)
        strange_layout.setContentsMargins(0, 0, 0, 0)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 5, 5, 5)
        strange_widget.setLayout(top_layout)

        self._button_plus = Button(self.tm, 'plus', css='Menu')
        self._button_plus.setFixedSize(26, 26)
        self._button_plus.clicked.connect(self.object_manager.new_layer)
        top_layout.addWidget(self._button_plus)

        self._scroll_area = QScrollArea()
        main_layout.addWidget(self._scroll_area)
        scroll_widget = QWidget()
        self._scroll_area.setWidget(scroll_widget)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_widget.setLayout(self._scroll_layout)

        self.object_manager.layerAdded.connect(self._on_add_layer)
        self.object_manager.layerDeleted.connect(self._on_layer_delete)
        self.object_manager.layerSelected.connect(self._on_layer_selected)
        self.object_manager.layerHiddenChanged.connect(self._on_layer_hidden_changed)

        for layer in object_manager.layers.values():
            self._on_add_layer(layer)
        self._on_layer_selected(self.object_manager.current_layer)

    def _on_add_layer(self, layer):
        item = LayerItem(self.tm, layer)
        item.set_styles()

        item.deleted.connect(self.object_manager.delete_layer)
        item.selected.connect(self.object_manager.select_layer)
        item.hiddenChanged.connect(self.object_manager.set_layer_hidden)
        item.nameChanged.connect(lambda layer_id, name: self.object_manager.set_layer_name(name, layer_id))
        item.colorChanged.connect(lambda layer_id, color: self.object_manager.set_layer_color(color, layer_id))

        self.items[layer.id] = item
        self._scroll_layout.addWidget(item)

    def _on_layer_delete(self, layer_id):
        self.items[layer_id].setParent(None)

    def _on_layer_hidden_changed(self, layer_id):
        self.items[layer_id].set_hidden(self.object_manager.layers[layer_id].hidden)

    def _on_layer_selected(self, layer_id):
        for i, item in self.items.items():
            if i == layer_id:
                item.set_selected(True)
            else:
                item.set_selected(False)

    def set_styles(self):
        self.setStyleSheet(self.tm.bg_style_sheet)
        self._top_widget.setStyleSheet(f"background-color: {self.tm['MenuColor']};"
                                       f"border-bottom: 1px solid {self.tm['BorderColor']};")
        self._button_plus.set_styles()
        self.tm.auto_css(self._scroll_area, palette='Bg', border=False)
        for el in self.items.values():
            el.set_styles()


class LayerItem(QWidget):
    nameChanged = pyqtSignal(UUID, str)
    selected = pyqtSignal(UUID)
    deleted = pyqtSignal(UUID)
    hiddenChanged = pyqtSignal(UUID, bool)
    colorChanged = pyqtSignal(UUID, ObjectColor)

    def __init__(self, tm, layer: Layer):
        super().__init__()
        self.tm = tm
        self._layer = layer

        strange_layout = QVBoxLayout()
        strange_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(strange_layout)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.setContentsMargins(4, 4, 4, 4)
        strange_widget.setLayout(main_layout)

        self._checkbox = QCheckBox()
        self._checkbox.setFixedSize(13, 13)
        self._checkbox.clicked.connect(self._on_selected)
        main_layout.addWidget(self._checkbox)

        self._name_edit = LineEdit(self.tm, layer.name)
        self._name_edit.setMaximumWidth(220)
        self._name_edit.editingFinished.connect(lambda: self.nameChanged.emit(self._layer.id, self._name_edit.text()))
        main_layout.addWidget(self._name_edit)

        self._button_hide = Button(self.tm, 'hide', css='Menu')
        self._button_hide.setFixedSize(22, 22)
        self._button_hide.clicked.connect(self._on_hide)
        main_layout.addWidget(self._button_hide)

        self._button_show = Button(self.tm, 'show', css='Menu')
        self._button_show.setFixedSize(22, 22)
        self._button_show.clicked.connect(self._on_show)
        main_layout.addWidget(self._button_show)

        if self._layer.hidden:
            self._button_hide.hide()
        else:
            self._button_show.hide()

        self._color_button = ColorButton(self.tm, _random=True)
        self._color_button.setFixedSize(32, 22)
        self._color_button.colorChanged.connect(lambda color: self.colorChanged.emit(self._layer.id, color))
        main_layout.addWidget(self._color_button)

        self._widget = QWidget()
        main_layout.addWidget(self._widget)

        self._button_delete = Button(self.tm, 'delete', css='Menu')
        self._button_delete.setFixedSize(22, 22)
        self._button_delete.clicked.connect(lambda: self.deleted.emit(self._layer.id))
        main_layout.addWidget(self._button_delete)

    def _on_hide(self):
        self._button_hide.hide()
        self._button_show.show()
        self.hiddenChanged.emit(self._layer.id, True)

    def _on_show(self):
        self._button_show.hide()
        self._button_hide.show()
        self.hiddenChanged.emit(self._layer.id, False)

    def set_hidden(self, flag):
        if flag:
            self._button_hide.hide()
            self._button_show.show()
        else:
            self._button_show.hide()
            self._button_hide.show()

    def _on_selected(self):
        if not self._checkbox.isChecked():
            self._checkbox.setChecked(True)
        else:
            self.selected.emit(self._layer.id)

    def set_selected(self, flag):
        self._checkbox.setChecked(flag)

    def set_styles(self):
        self.setStyleSheet(self.tm.base_css(palette='Menu'))
        self._widget.setStyleSheet('border: none;')
        for el in [self._checkbox, self._button_show, self._button_hide, self._button_delete]:
            self.tm.auto_css(el)
        self._color_button.set_styles()
        self._name_edit.set_styles()
