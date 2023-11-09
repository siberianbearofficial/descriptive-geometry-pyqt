from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from utils.ui.widgets.button import Button
from utils.ui.widgets.layer_box import LayerBox


class TopBar(QWidget):
    intersectionClicked = pyqtSignal()
    inversionChanged = pyqtSignal(bool)

    def __init__(self, theme_manager, object_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.object_manager = object_manager
        self.setFixedHeight(40)

        strange_layout = QHBoxLayout()
        strange_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(strange_layout)
        strange_widget = QWidget()
        strange_layout.addWidget(strange_widget)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        strange_widget.setLayout(layout)

        self.button_ruler = TopBarButton(self.theme_manager, 'ruler', tooltip='Расстояние')
        layout.addWidget(self.button_ruler)

        self.button_angle = TopBarButton(self.theme_manager, 'angle', tooltip='Угол')
        layout.addWidget(self.button_angle)

        self.button_intersection = TopBarButton(self.theme_manager, 'intersection', tooltip='Пересечение')
        self.button_intersection.clicked.connect(self.intersectionClicked.emit)
        layout.addWidget(self.button_intersection)

        self.layer_box = LayerBox(self.theme_manager, self.object_manager)
        layout.addWidget(self.layer_box)

        self.plane_box = PlaneIndicator(self.theme_manager)
        self.plane_box.inversionChanged.connect(self.inversionChanged.emit)
        layout.addWidget(self.plane_box)

        self._widget = QWidget()
        layout.addWidget(self._widget, 100)

        self.button_authorization = TopBarButton(self.theme_manager, 'authorization', tooltip='Авторизация')
        layout.addWidget(self.button_authorization, 1, Qt.AlignmentFlag.AlignRight)

        self.button_settings = TopBarButton(self.theme_manager, 'settings', tooltip='Настройки')
        layout.addWidget(self.button_settings, 1, Qt.AlignmentFlag.AlignRight)

    def set_styles(self):
        self.setStyleSheet(f"background-color: {self.theme_manager['MenuColor']};"
                           f"border-top: 1px solid {self.theme_manager['BorderColor']};"
                           f"border-bottom: 1px solid {self.theme_manager['BorderColor']};")
        for el in [self.button_ruler, self.button_angle, self.button_intersection, self.button_settings,
                   self.button_authorization]:
            self.theme_manager.auto_css(el)
        self.layer_box.set_styles()
        self.plane_box.set_styles()
        self._widget.setStyleSheet('border: none;')


class TopBarButton(Button):
    def __init__(self, theme_manager, image, tooltip):
        super().__init__(theme_manager, image, css='Menu', tooltip=tooltip)
        self.setFixedSize(30, 30)


class PlaneIndicator(QWidget):
    inversionChanged = pyqtSignal(bool)

    def __init__(self, tm):
        super().__init__()
        self.tm = tm

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.button_xy = QPushButton('XY')
        self.button_xy.setCheckable(True)
        self.button_xy.setChecked(True)
        self.button_xy.setFixedSize(28, 24)
        self.button_xy.clicked.connect(self._on_xy_clicked)
        layout.addWidget(self.button_xy)

        self.button_xz = QPushButton('XZ')
        self.button_xz.setCheckable(True)
        self.button_xz.setFixedSize(28, 24)
        self.button_xz.clicked.connect(self._on_xz_clicked)
        layout.addWidget(self.button_xz)

    def _on_xy_clicked(self, flag):
        if flag:
            self.button_xz.setChecked(False)
            self.inversionChanged.emit(False)
        self.button_xy.setChecked(True)

    def _on_xz_clicked(self, flag):
        if flag:
            self.button_xy.setChecked(False)
            self.inversionChanged.emit(True)
        self.button_xz.setChecked(True)

    def set_styles(self):
        self.button_xy.setFont(self.tm.font_medium)
        self.button_xz.setFont(self.tm.font_medium)
        self.button_xy.setStyleSheet(self.tm.button_css(palette='Menu', border=True, br_right=False))
        self.button_xz.setStyleSheet(self.tm.button_css(palette='Menu', border=True, br_left=False))
