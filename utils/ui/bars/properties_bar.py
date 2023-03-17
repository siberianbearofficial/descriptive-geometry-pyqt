from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QLayout, QComboBox, \
    QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from utils.ui.bars.properties_bar_object import PropertiesBarObject
from utils.ui.widgets.LineEditWidget import LineEditWidget
from utils.ui.widgets.widget import Widget


class PropertiesBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.current_object = None
        self.set_obj_name = None
        self.set_obj_color = None
        self.set_obj_thickness = None
        self.set_obj_layer = None
        self.set_obj_ag_object = None
        self.set_obj_config = None
        self.layers_list = []
        self.font_manager = font_manager

        self.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # Name
        name = QVBoxLayout()
        name_label = QLabel(self.central_widget)
        name_label.setFixedHeight(20)

        name_label.setFont(font_manager.bold())
        name_label.setStyleSheet("color: #00ABB3;")
        name_label.setText('Name')
        name.addWidget(name_label)

        self.name_line_edit = LineEditWidget(self.central_widget)
        self.name_line_edit.setFixedHeight(30)
        self.name_line_edit.setFont(font_manager.bold())
        self.name_line_edit.setStyleSheet("color: #00ABB3;\n"
                                          "background-color: #EAEAEA;\n"
                                          "border: 2px solid #00ABB3;\n"
                                          "padding-left: 3px;")
        self.name_line_edit.connect(lambda: self.on_name_change(self.name_line_edit.text()))
        name.addWidget(self.name_line_edit)

        self.layout.addLayout(name)

        # Color, Layer, Thickness
        self.clt = QHBoxLayout()
        self.clt.setSpacing(10)
        self.clt.setAlignment(Qt.AlignLeft)

        # Color
        color = QVBoxLayout()
        color.setSpacing(5)

        color_label = QLabel(self.central_widget)
        color_label.setFixedHeight(20)
        color_label.setFont(font_manager.bold())
        color_label.setStyleSheet("color: #00ABB3;")
        color_label.setText('Color')
        color.addWidget(color_label)

        self.color_button = QPushButton(self.central_widget)
        self.color_button.setFixedSize(30, 30)
        self.color_button.setStyleSheet("color: #00ABB3;\n"
                                        "background-color: #CCFCE5;\n"
                                        "border: 2px solid #00ABB3;\n"
                                        "padding-top: 3px;")
        self.color_button_stylesheet = self.color_button.styleSheet().split('\n')
        self.color_button.setText("")
        self.color_button.clicked.connect(self.on_color_change)

        color.addWidget(self.color_button)

        self.clt.addLayout(color)

        # Layer
        layer = QVBoxLayout()
        layer.setSizeConstraint(QLayout.SetMinimumSize)
        layer.setSpacing(5)

        layer_label = QLabel(self.central_widget)
        layer_label.setFixedHeight(20)
        layer_label.setFont(font_manager.bold())
        layer_label.setStyleSheet("color: #00ABB3;")
        layer_label.setText('Layer')
        layer.addWidget(layer_label)

        self.layer_line_edit = QLineEdit(self.central_widget)
        self.layer_line_edit.setFixedSize(30, 30)
        self.layer_line_edit.setFont(font_manager.bold())
        self.layer_line_edit.setAcceptDrops(False)
        self.layer_line_edit.setStyleSheet("color: #00ABB3;\n"
                                           "background-color: #EAEAEA;\n"
                                           "border: 2px solid #00ABB3;")
        self.layer_line_edit.setAlignment(Qt.AlignCenter)
        self.layer_line_edit.editingFinished.connect(lambda: self.on_layer_change(self.layer_line_edit.text()))
        layer.addWidget(self.layer_line_edit)

        self.clt.addLayout(layer)

        # Thickness
        thickness = QVBoxLayout()
        thickness.setSpacing(5)

        thickness_label = QLabel(self.central_widget)
        thickness_label.setFixedHeight(20)
        thickness_label.setFont(font_manager.bold())
        thickness_label.setStyleSheet("color: #00ABB3;")
        thickness_label.setText('Thickness')
        thickness.addWidget(thickness_label)

        self.thickness_combobox = QComboBox(self.central_widget)
        self.thickness_combobox.setFixedSize(70, 30)
        self.thickness_combobox.setFont(font_manager.bold())
        self.thickness_combobox.setLayoutDirection(Qt.RightToLeft)
        self.thickness_combobox.setStyleSheet("QComboBox {\n"
                                              "color: #00ABB3;\n"
                                              "background-color: #EAEAEA;\n"
                                              "border: 2px solid #00ABB3;\n"
                                              "padding-right: 1px;\n"
                                              "}\n"
                                              "QComboBox::drop-down:button {\n"
                                              "border-radius: 5px;\n"
                                              "}")
        self.thickness_combobox.setMaxVisibleItems(3)
        self.thickness_combobox.addItem("light")
        self.thickness_combobox.addItem("medium")
        self.thickness_combobox.addItem("bold")
        self.thickness_combobox.currentIndexChanged.connect(
            lambda: self.on_thickness_change(self.thickness_combobox.currentIndex() + 1))
        thickness.addWidget(self.thickness_combobox)
        self.clt.addLayout(thickness)
        self.layout.addLayout(self.clt)

        self.obj_layout = QVBoxLayout()
        self.layout.addLayout(self.obj_layout)

        self.obj = None

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

    def on_layer_change(self, layer):
        if self.set_obj_layer:
            self.set_obj_layer(layer=layer)

    def update_layers_widget(self, *args):
        print(self.layers_list)

    def on_color_change(self):
        if self.set_obj_color:
            color = QColorDialog.getColor(QColor(*self.current_object.color))
            self.change_stylesheet(self.color_button, f'background-color: rgba{color.getRgb()};')
            self.set_obj_color(color=color.getRgb())

    def change_stylesheet(self, obj=None, new_style_sheet=None):
        self.color_button_stylesheet[1] = new_style_sheet
        self.color_button.setStyleSheet('\n'.join(self.color_button_stylesheet))
        # print('\n'.join(self.color_button_stylesheet))

    def on_thickness_change(self, thickness):
        if self.set_obj_thickness:
            self.set_obj_thickness(thickness=thickness)

    def on_name_change(self, name):
        if self.set_obj_name:
            self.set_obj_name(name=name)

    def open_object(self, obj):
        if obj:
            # print('Object:', obj)
            self.current_object = obj
            self.show_object()
            self.show()
        elif self.current_object:
            self.clear_objects()
            self.hide()

    def clear_objects(self):
        for i in range(self.obj_layout.count() - 1, -1, -1):
            self.obj_layout.itemAt(i).widget().deleteLater()

    def show_objects(self, struct):
        self.clear_objects()
        self.obj = PropertiesBarObject(struct=struct['ag_object'], parent=self.central_widget,
                                       font_manager=self.font_manager, name='Objects')
        self.obj_layout.addWidget(self.obj)

    def show_object(self):
        self.name_line_edit.setText(self.current_object.name)
        self.change_stylesheet(self.color_button, f'background-color: rgb{self.current_object.color};')
        self.thickness_combobox.setCurrentIndex(self.current_object.thickness - 1)
        self.thickness_combobox.setDisabled(False)

        self.show_objects(self.current_object.to_dict())

    def hide(self):
        super().hide()
        return self

    def clear(self):
        self.current_object = None
        self.name_line_edit.clear()
        self.thickness_combobox.setCurrentIndex(0)
        self.thickness_combobox.setDisabled(True)
        self.layer_line_edit.clear()
