from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QTransform
from utils.ui.widgets.widget import Widget
from utils.color import *


class InspectorBarObject(Widget):
    EYE_SIZE = 20
    EYE_PIXMAP = None

    def __init__(self, obj, parent, font_manager, hide_func, select_func):
        super().__init__(parent)

        self.hide_func = hide_func
        self.select_func = select_func

        if not InspectorBarObject.EYE_PIXMAP:
            InspectorBarObject.EYE_PIXMAP = QPixmap(":/img/img/inspector_bar_object_icon.png")

        # Layout
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Icon
        icon = Eye(self)
        self.layout.addWidget(icon)

        # Label
        self.label = QLabel(self.central_widget)
        self.label.setFont(font_manager.bold())
        self.label.setStyleSheet(f"color: {ACCENT_COLOR};")
        self.label.setText(f'{obj.ag_object.__class__.__name__}: {obj.name}')
        self.layout.addWidget(self.label)

        self.obj_hidden = False
        self.obj = obj

    def select(self, revert=False):
        if not revert:
            self.label.setStyleSheet(f"color: {DARK_COLOR};")
        else:
            self.label.setStyleSheet(f"color: {ACCENT_COLOR};")

    def mousePressEvent(self, a0):
        if a0.button() == 1:
            if self.select_func:
                self.select_func(self)


class Eye(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.opened_pixmap = InspectorBarObject.EYE_PIXMAP
        self.closed_pixmap = InspectorBarObject.EYE_PIXMAP.transformed(QTransform().rotate(90))
        self.opened = True

        self.setFixedSize(InspectorBarObject.EYE_SIZE, InspectorBarObject.EYE_SIZE)
        self.setPixmap(self.opened_pixmap)
        self.setScaledContents(True)

        if parent.hide_func:
            self.hide_func = parent.hide_func
        else:
            self.hide_func = None

    def mousePressEvent(self, ev):
        if ev.button() == 1:
            if self.hide_func:
                self.opened = not self.opened
                self.setPixmap(self.opened_pixmap if self.opened else self.closed_pixmap)
                self.hide_func(self.opened)

    def set_on_click_listener(self, func):
        self.hide_func = func
        return self
