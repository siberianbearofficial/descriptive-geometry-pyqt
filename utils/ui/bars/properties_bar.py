from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLayout, QComboBox, \
    QColorDialog, QScrollArea, QWidget, QLineEdit
from PyQt6.QtCore import Qt

from utils.ui.bars.properties_bar_object import PropertiesBarObject
from utils.ui.widgets.color_button import ColorButton
from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *
from utils.thickness import *


class PropertiesBar(QWidget):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self._labels = []
        self.mouse_pos = None

        self.setFixedSize(250, 350)
        self.setWindowFlag(Qt.WindowType.Tool, True)

        strange_layout = QHBoxLayout()
        self.setLayout(strange_layout)
        strange_layout.setContentsMargins(0, 0, 0, 0)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        strange_widget.setLayout(main_layout)

        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self._name_edit = QLineEdit()
        main_layout.addWidget(self._name_edit)

        layer_layout = QHBoxLayout()
        layer_layout.setContentsMargins(0, 0, 0, 0)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(layer_layout)

        label = QLabel("Слой:")
        self._labels.append(label)
        layer_layout.addWidget(label)

        self._layer_box = QComboBox()
        self._layer_box.setMinimumWidth(120)
        layer_layout.addWidget(self._layer_box)

        color_layout = QHBoxLayout()
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(color_layout)

        self._color_button = ColorButton(self.theme_manager)
        self._color_button.setFixedSize(50, 22)
        color_layout.addWidget(self._color_button)

    def set_obj_name_func(self, func):
        self.set_obj_name = func
        return self

    def set_obj_color_func(self, func):
        self.set_obj_color = func
        return self

    def set_obj_layer_func(self, func):
        self.set_obj_layer = func
        return self

    def set_obj_thickness_func(self, func):
        self.set_obj_thickness = func
        return self

    def set_obj_ag_object_func(self, func):
        self.set_obj_ag_object = func
        return self

    def set_obj_config_func(self, func):
        self.set_obj_config = func
        return self

    def set_layers_list(self, layers_list):
        self.layers_list = layers_list
        return self

    def update_layers_widget(self, *args):
        self.layer_combobox.clear()
        for layer in self.layers_list:
            self.layer_combobox.addItem(layer.name)

    def on_layer_change(self, layer):
        if self.set_obj_layer and layer >= 0:
            self.set_obj_layer(int(layer))

    def on_color_change(self):
        if self.set_obj_color:
            color = Color(QColorDialog.getColor(self.current_object.color))
            self.change_stylesheet(self.color_button, f'background-color: {color};')
            self.set_obj_color(color=color)

    def change_stylesheet(self, obj=None, new_style_sheet=None):
        self.color_button_stylesheet[1] = new_style_sheet
        self.color_button.setStyleSheet('\n'.join(self.color_button_stylesheet))
        # print('\n'.join(self.color_button_stylesheet))

    def on_thickness_change(self, thickness):
        if self.set_obj_thickness:
            match thickness:
                case 0:
                    self.set_obj_thickness(thickness=Thickness.LIGHT_THICKNESS)
                case 1:
                    self.set_obj_thickness(thickness=Thickness.MEDIUM_THICKNESS)
                case 2:
                    self.set_obj_thickness(thickness=Thickness.BOLD_THICKNESS)
                case _:
                    self.set_obj_thickness(thickness=Thickness.fix(thickness))

    def on_name_change(self, name):
        if self.set_obj_name:
            self.set_obj_name(name=name)

    def on_ag_object_change(self, path, value):
        self.set_obj_ag_object(self.change_current_object_dict(path, value, self.current_object.to_dict()['ag_object']))

    def change_current_object_dict(self, path, value, dct):
        if len(path) == 1:
            dct[path[0]] = value
            return dct
        dct.update({path[0]: self.change_current_object_dict(path[1:], value, dct[path[0]])})
        return dct

    def open_object(self, obj):
        if obj:
            # print('Object:', obj)
            self.current_object = obj
            self.show_object()
            self.show()
        elif self.current_object:
            self.clear_objects()
            self.hide()
            self.current_object = None

    def clear_objects(self):
        for i in range(self.obj_layout.count() - 1, -1, -1):
            self.obj_layout.itemAt(i).widget().deleteLater()

    def show_objects(self, struct):
        self.clear_objects()
        self.obj = PropertiesBarObject(struct=struct['ag_object'], parent=self.central_widget,
                                       font_manager=self.font_manager, name='Objects',
                                       on_editing_finished=self.on_ag_object_change).set_margin(0)
        self.obj_layout.addWidget(self.obj)

    def thickness_to_ind(self, thickness):
        match thickness:
            case Thickness.LIGHT_THICKNESS:
                return 0
            case Thickness.MEDIUM_THICKNESS:
                return 1
            case Thickness.BOLD_THICKNESS:
                return 2
            case _:
                return self.thickness_to_ind(Thickness.fix(thickness))

    def show_object(self):
        self.name_line_edit.setText(self.current_object.name)
        self.change_stylesheet(self.color_button, f'background-color: {self.current_object.color};')

        self.thickness_combobox.setCurrentIndex(self.thickness_to_ind(self.current_object.thickness))

        match self.current_object.thickness:
            case Thickness.LIGHT_THICKNESS:
                self.thickness_combobox.setCurrentIndex(0)
            case Thickness.MEDIUM_THICKNESS:
                self.thickness_combobox.setCurrentIndex(1)
            case Thickness.BOLD_THICKNESS:
                self.thickness_combobox.setCurrentIndex(2)
            case _:
                self.current_object.thickness = Thickness.fix(self.current_object.thickness)

        self.layer_combobox.setCurrentIndex(0)  # TODO: set current layer
        self.show_objects(self.current_object.to_dict())

    def hide(self):
        super().hide()
        return self

    def clear(self):
        self.current_object = None
        self.name_line_edit.clear()
        self.thickness_combobox.setCurrentIndex(0)

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
        for el in self._labels:
            self.theme_manager.auto_css(el)
        for el in [self._name_edit, self._layer_box]:
            self.theme_manager.auto_css(el)
        self._color_button.set_styles()
