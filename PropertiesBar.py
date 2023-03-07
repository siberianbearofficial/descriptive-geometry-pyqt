from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QLayout, QComboBox, \
    QColorDialog
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class PropertiesBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.current_object = None

        self.setGeometry(889, 150, 171, 331)
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        self.strange_widget = QWidget(self)
        self.strange_widget.setFixedSize(self.geometry().size())

        self.layout = QVBoxLayout(self.strange_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(15, 15, 15, 15)

        font = QFont()
        font.setFamily("Alegreya Sans SC ExtraBold")
        font.setPointSize(7)

        # Name
        name = QVBoxLayout()
        name_label = QLabel(self.strange_widget)
        name_label.setFixedHeight(20)

        name_label.setFont(font)
        name_label.setStyleSheet("color: #00ABB3;")
        name_label.setText('Name')
        name.addWidget(name_label)

        self.name_line_edit = QLineEdit(self.strange_widget)
        self.name_line_edit.setFixedHeight(30)
        self.name_line_edit.setFont(font)
        self.name_line_edit.setStyleSheet("color: #00ABB3;\n"
                                          "background-color: #EAEAEA;\n"
                                          "border: 2px solid #00ABB3;\n"
                                          "padding-left: 3px;")
        self.name_line_edit.editingFinished.connect(lambda: self.on_name_change(self.name_line_edit.text()))
        name.addWidget(self.name_line_edit)

        self.layout.addLayout(name)

        # Color, Layer, Thickness
        self.clt = QHBoxLayout()
        self.clt.setSpacing(5)

        # Color
        color = QVBoxLayout()
        color.setSpacing(5)

        color_label = QLabel(self.strange_widget)
        color_label.setFixedHeight(20)
        color_label.setFont(font)
        color_label.setStyleSheet("color: #00ABB3;")
        color_label.setText('Color')
        color.addWidget(color_label)

        self.color_button = QPushButton(self.strange_widget)
        self.color_button.setFixedSize(30, 30)
        self.color_button.setStyleSheet("color: #00ABB3;\n"
                                        "background-color: #CCFCE5;\n"
                                        "border: 2px solid #00ABB3;\n"
                                        "padding-top: 3px;")
        self.color_button_stylesheet = self.color_button.styleSheet().split('\n')
        self.color_button.setText("")
        self.color_button.clicked.connect(lambda: self.on_color_change((0, 0, 255)))
        color.addWidget(self.color_button)

        self.clt.addLayout(color)

        # Layer
        layer = QVBoxLayout()
        layer.setSizeConstraint(QLayout.SetMinimumSize)
        layer.setSpacing(5)

        layer_label = QLabel(self.strange_widget)
        layer_label.setFixedHeight(20)
        layer_label.setFont(font)
        layer_label.setStyleSheet("color: #00ABB3;")
        layer_label.setText('Layer')
        layer.addWidget(layer_label)

        self.layer_line_edit = QLineEdit(self.strange_widget)
        self.layer_line_edit.setFixedSize(30, 30)
        self.layer_line_edit.setFont(font)
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

        thickness_label = QLabel(self.strange_widget)
        thickness_label.setFixedHeight(20)
        thickness_label.setFont(font)
        thickness_label.setStyleSheet("color: #00ABB3;")
        thickness_label.setText('Thickness')
        thickness.addWidget(thickness_label)

        self.thickness_combobox = QComboBox(self.strange_widget)
        self.thickness_combobox.setFixedSize(70, 30)
        self.thickness_combobox.setFont(font)
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

        # self.properties_bar_objects = QtWidgets.QVBoxLayout()
        # self.properties_bar_objects.setObjectName("properties_bar_objects")
        # self.properties_bar_object_1 = QtWidgets.QWidget(self.strange_widget)
        # self.properties_bar_object_1.setObjectName("properties_bar_object_1")
        # self.widget4 = QtWidgets.QWidget(self.properties_bar_object_1)
        # self.widget4.setGeometry(QtCore.QRect(0, 0, 139, 23))
        # self.widget4.setObjectName("widget4")
        # self.properties_bar_object_1_layout = QtWidgets.QHBoxLayout(self.widget4)
        # self.properties_bar_object_1_layout.setContentsMargins(0, 0, 0, 0)
        # self.properties_bar_object_1_layout.setSpacing(5)
        # self.properties_bar_object_1_layout.setObjectName("properties_bar_object_1_layout")
        # self.properties_bar_object_1_icon = QtWidgets.QLabel(self.widget4)
        # self.properties_bar_object_1_icon.setMaximumSize(QtCore.QSize(20, 20))
        # self.properties_bar_object_1_icon.setText("")
        # self.properties_bar_object_1_icon.setPixmap(QtGui.QPixmap(":/img/img/inspector_bar_object_icon.png"))
        # self.properties_bar_object_1_icon.setScaledContents(True)
        # self.properties_bar_object_1_icon.setObjectName("properties_bar_object_1_icon")
        # self.properties_bar_object_1_layout.addWidget(self.properties_bar_object_1_icon)
        # self.properties_bar_object_1_label = QtWidgets.QLabel(self.widget4)
        # self.properties_bar_object_1_label.setMaximumSize(QtCore.QSize(16777215, 20))
        # font = QtGui.QFont()
        # font.setFamily("Alegreya Sans SC ExtraBold")
        # font.setPointSize(7)
        # self.properties_bar_object_1_label.setFont(font)
        # self.properties_bar_object_1_label.setStyleSheet("color: #00ABB3;")
        # self.properties_bar_object_1_label.setObjectName("properties_bar_object_1_label")
        # self.properties_bar_object_1_layout.addWidget(self.properties_bar_object_1_label)
        # self.properties_bar_objects.addWidget(self.properties_bar_object_1)
        # self.properties_bar_layout.addLayout(self.properties_bar_objects)

    def on_layer_change(self, layer):
        # print('Layer:', layer)
        self.save(self.current_object, layer=layer)

    def on_color_change(self, color):
        # print('Color:', color)
        color = QColorDialog(QColor(*self.current_object.color), self).getColor()
        self.change_stylesheet(self.color_button, f'background-color: rgba{color.getRgb()};')
        self.save(self.current_object, color=color.getRgb())

    def change_stylesheet(self, obj=None, new_style_sheet=None):
        self.color_button_stylesheet[1] = new_style_sheet
        self.color_button.setStyleSheet('\n'.join(self.color_button_stylesheet))
        print('\n'.join(self.color_button_stylesheet))

    def on_thickness_change(self, thickness):
        # print('Thickness:', thickness)
        self.save(self.current_object, thickness=thickness)

    def on_name_change(self, name):
        print('Name:', name)
        self.save(self.current_object, name=name)

    def open_object(self, obj):
        if obj:
            # print('Object:', obj)
            self.current_object = obj
            self.show_object()
            self.show()
        elif self.current_object:
            self.save(self.current_object, name=self.current_object.name, color=None,
                      thickness=self.current_object.thickness, layer=None)
            self.clear()
            self.hide()

    def show_object(self):
        self.name_line_edit.setText(self.current_object.name)
        self.change_stylesheet(self.color_button, f'background-color: rgb{self.current_object.color};')
        # self.layer_line_edit.setText(self.current_object.layer)
        self.thickness_combobox.setCurrentIndex(self.current_object.thickness - 1)
        self.thickness_combobox.setDisabled(False)

    def clear(self):
        self.current_object = None
        self.name_line_edit.clear()
        self.thickness_combobox.setCurrentIndex(0)
        self.thickness_combobox.setDisabled(True)
        self.layer_line_edit.clear()
        # self.color_button.clear()
