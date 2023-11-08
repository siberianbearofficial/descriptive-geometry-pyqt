from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QLineEdit, QApplication, QDoubleSpinBox
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform

from core.config import CANVASS_X
from utils.ui.widgets.button import Button
from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *


class PropertiesBarObject(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, theme_manager, name, struct: dict[str: dict | int | float] | int | float):
        super().__init__()
        self.tm = theme_manager
        self.name = name
        self.struct = struct

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_layout)

        self._down_arrow = Button(self.tm, 'down_arrow', css='Menu')
        self._down_arrow.setFixedSize(18, 18)
        self._down_arrow.clicked.connect(self.hide_children)
        self._down_arrow.hide()
        top_layout.addWidget(self._down_arrow)

        self._right_arrow = Button(self.tm, 'right_arrow', css='Menu')
        self._right_arrow.setFixedSize(18, 18)
        self._right_arrow.clicked.connect(self.show_children)
        self._right_arrow.hide()
        top_layout.addWidget(self._right_arrow)

        self._name_label = QLabel(self.name)
        top_layout.addWidget(self._name_label)

        self._spin_box = QDoubleSpinBox()
        self._spin_box.hide()
        self._spin_box.setRange(-CANVASS_X // 2, CANVASS_X // 2)
        self._spin_box.valueChanged.connect(self._on_value_changed)
        top_layout.addWidget(self._spin_box)

        self._children_layout = QVBoxLayout()
        self._children_layout.setContentsMargins(20, 0, 0, 0)
        main_layout.addLayout(self._children_layout)

        self.children = dict()
        if isinstance(self.struct[self.name], dict):
            self._down_arrow.show()
            for key, item in self.struct[self.name].items():
                if key == 'class':
                    continue
                widget = PropertiesBarObject(self.tm, key, self.struct[self.name])
                widget.valueChanged.connect(self.valueChanged.emit)
                self.children[key] = widget
                self._children_layout.addWidget(widget)
        elif isinstance(self.struct[self.name], (int, float)):
            self._spin_box.show()
            self._spin_box.setValue(self.struct[self.name])

    def _on_value_changed(self):
        self.struct[self.name] = self._spin_box.value()
        self.valueChanged.emit()

    def show_children(self):
        self._right_arrow.hide()
        self._down_arrow.show()
        for el in self.children.values():
            el.show()

    def hide_children(self):
        self._down_arrow.hide()
        self._right_arrow.show()
        for el in self.children.values():
            el.hide()

    def set_styles(self):
        for el in [self._name_label, self._down_arrow, self._right_arrow, self._spin_box]:
            self.tm.auto_css(el)
        for el in self.children.values():
            if isinstance(el, PropertiesBarObject):
                el.set_styles()
            else:
                self.tm.auto_css(el)
