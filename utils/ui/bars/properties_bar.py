from uuid import UUID

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLayout, QComboBox, \
    QColorDialog, QScrollArea, QWidget, QLineEdit
from PyQt6.QtCore import Qt

from utils.objects.general_object import GeneralObject
from utils.objects.object_manager import ObjectManager
from utils.ui.bars.properties_bar_object import PropertiesBarObject
from utils.ui.widgets.button import Button
from utils.ui.widgets.color_button import ColorButton
from utils.ui.widgets.line_edit import LineEdit
from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *
from utils.thickness import *


class PropertiesBar(QWidget):
    def __init__(self, theme_manager, object_manager: ObjectManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.object_manager = object_manager
        self._labels = []
        self.object = None
        self.object_dict = None
        self.mouse_pos = None

        self.setFixedSize(250, 350)
        self.setWindowFlag(Qt.WindowType.Tool, True)

        strange_layout = QHBoxLayout()
        self.setLayout(strange_layout)
        strange_layout.setContentsMargins(0, 0, 0, 0)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 4)
        strange_widget.setLayout(main_layout)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(7, 7, 5, 7)
        main_layout.addLayout(top_layout)

        self._object_label = QLabel()
        top_layout.addWidget(self._object_label)

        self._button_close = Button(self.theme_manager, 'delete')
        self._button_close.setFixedSize(28, 28)
        self._button_close.clicked.connect(self.hide)
        top_layout.addWidget(self._button_close, 1, Qt.AlignmentFlag.AlignRight)

        self._scroll_area = QScrollArea()
        main_layout.addWidget(self._scroll_area)
        self._scroll_widget = QWidget()
        self._scroll_area.setWidget(self._scroll_widget)
        self._scroll_area.setWidgetResizable(True)

        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll_widget.setLayout(scroll_layout)

        # self._name_edit = LineEdit(self.theme_manager)
        self._name_edit = QLineEdit()
        scroll_layout.addWidget(self._name_edit)

        layer_layout = QHBoxLayout()
        layer_layout.setContentsMargins(0, 0, 0, 0)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll_layout.addLayout(layer_layout)

        label = QLabel("Слой:")
        self._labels.append(label)
        layer_layout.addWidget(label)

        self._layer_box = QComboBox()
        self._layer_box.setMinimumWidth(120)
        layer_layout.addWidget(self._layer_box)

        color_layout = QHBoxLayout()
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll_layout.addLayout(color_layout)

        self._color_button = ColorButton(self.theme_manager, layer=True)
        self._color_button.setFixedSize(50, 22)
        self._color_button.colorChanged.connect(self._on_color_changed)
        color_layout.addWidget(self._color_button)

        self.object_items = dict()
        self.children_layout = QVBoxLayout()
        scroll_layout.addLayout(self.children_layout)

        self.object_manager.objectSelected.connect(self.open_object)

    def open_object(self, obj_id: UUID | None):
        if obj_id is None:
            self.object = None
            self.hide()
            for el in self.object_items.values():
                el.setParent(None)
            self.object_items.clear()
        else:
            self.object = self.object_manager.get_object(obj_id)
            self.object_dict = self.object.to_dict()
            self.show()
            self._object_label.setText(self.object.ag_object.__class__.__name__)
            self._name_edit.setText(self.object.name)
            self._color_button.set_color(self.object.color)
            for key, item in self.object_dict['ag_object'].items():
                if key == 'class':
                    continue
                self.children_layout.addWidget(widget := PropertiesBarObject(
                    self.theme_manager, key, self.object_dict['ag_object']))
                self.object_items[key] = widget
                widget.valueChanged.connect(self._on_ag_obj_changed)
            self.set_styles()

    def _on_ag_obj_changed(self):
        self.object_manager.set_object_ag_obj(self.object_dict['ag_object'])

    def _on_color_changed(self, color):
        self.object_manager.set_object_color(color)

    def mousePressEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.mouse_pos = a0.pos()
        else:
            super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.mouse_pos = None
        else:
            super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0) -> None:
        if self.mouse_pos is not None:
            pos = self.pos() + a0.pos() - self.mouse_pos
            if pos.x() < 5:
                pos.setX(5)
            if pos.y() < 5:
                pos.setY(5)
            if pos.x() > self.parent().width() - self.width() - 15:
                pos.setX(self.parent().width() - self.width() - 15)
            if pos.y() > self.parent().height() - self.height() - 15:
                pos.setY(self.parent().height() - self.height() - 15)
            self.move(pos)
        else:
            super().mouseMoveEvent(a0)

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.base_css(palette='Menu'))
        self._scroll_widget.setStyleSheet('border: none;')
        self.theme_manager.auto_css(self._scroll_area, border=False, palette='Menu')
        self._scroll_area.setStyleSheet('border: none;')
        for el in self._labels:
            self.theme_manager.auto_css(el)
        for el in [self._layer_box, self._object_label, self._button_close, self._name_edit]:
            self.theme_manager.auto_css(el)
        for el in self.object_items.values():
            el.set_styles()
        # self._name_edit.set_styles()
        self._color_button.set_styles()
