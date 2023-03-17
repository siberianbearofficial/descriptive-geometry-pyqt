from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QMouseEvent

from utils.ui.widgets.LineEditWidget import LineEditWidget
from utils.ui.widgets.widget import Widget

from random import randint


class PropertiesBarObject(Widget):
    def __init__(self, struct=None, parent=None, margin=0, font_manager=None, name=None):
        super().__init__(parent)

        self.font_manager = font_manager
        self.margin = margin

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(margin, 0, 0, 0)
        self.layout.setSpacing(0)

        hor_layout = QHBoxLayout()

        self.icon = Image(20, 20, QPixmap(":/img/img/inspector_bar_object_icon.png"),
                          self.central_widget).set_on_click_listener(self.clicked)

        hor_layout.addWidget(self.icon)

        self.label = QLabel(self.central_widget)
        self.label.setMaximumHeight(20)
        if font_manager:
            self.label.setFont(font_manager.bold())
        self.label.setStyleSheet("color: #00ABB3;")
        if name:
            self.label.setText(name)
        hor_layout.addWidget(self.label)

        self.layout.addLayout(hor_layout)

        self.objects_widget = QWidget(self.central_widget)
        self.objects = QVBoxLayout(self.objects_widget)
        self.objects.setContentsMargins(0, 0, 0, 0)
        self.objects.setSpacing(0)
        self.unpack_objects_struct(struct)
        self.layout.addWidget(self.objects_widget)

        self.clicked()

    def unpack_objects_struct(self, struct):
        if isinstance(struct, dict):
            for key, item in struct.items():
                if key != 'class':
                    widget = PropertiesBarObject(struct=item,
                                                 parent=self.central_widget,
                                                 font_manager=self.font_manager,
                                                 margin=(self.margin + 10),
                                                 name=key)
                    self.objects.addWidget(widget)
        elif isinstance(struct, float):
            self.icon.hide()
            self.label.setText(f'{self.label.text()}: {struct}')

    def clicked(self):
        self.objects_widget.show() if self.objects_widget.isHidden() else self.objects_widget.hide()


class Image(QLabel):
    def __init__(self, width, height, pixmap, parent=None):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        self.clicked = None

        self.setMaximumSize(width, height)
        self.setPixmap(pixmap)
        self.setScaledContents(True)

    def mousePressEvent(self, ev):
        if ev.button() == 1:
            if self.clicked:
                self.clicked()

    def set_on_click_listener(self, func):
        self.clicked = func
        return self
