from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QWidget
from PyQt6.QtCore import Qt
from utils.ui.bars.inspector_bar_object import InspectorBarObject
from utils.color import *


class InspectorBar(QWidget):
    def __init__(self, parent, font_manager, theme_manager):
        super().__init__(parent)

        self.font_manager = font_manager
        self.theme_manager = theme_manager

        self.setStyleSheet(f"background-color: {LIGHT_COLOR}; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.objects_scroll_area = QScrollArea(self.central_widget)
        self.objects_scroll_area.setWidgetResizable(True)
        self.objects_scroll_area.verticalScrollBar().setStyleSheet('QScrollBar {height: 0px;}')

        self.objects_central_widget = QWidget()

        self.objects_layout = QVBoxLayout(self.objects_central_widget)
        self.objects_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.objects_layout.setContentsMargins(0, 0, 0, 0)
        self.objects_layout.setSpacing(0)

        self.objects_scroll_area.setWidget(self.objects_central_widget)

        self.layout.addWidget(self.objects_scroll_area)

        self.object_hidden = None
        self.change_current_object = None

        self.objects = list()

    def set_change_current_object_func(self, func):
        if func:
            self.change_current_object = func
        return self

    def set_object_hidden_func(self, func):
        if func:
            self.object_hidden = func
        return self

    def set_objects(self, objects):
        self.clear_layout()
        self.objects.clear()
        for obj in objects:
            ib_obj = InspectorBarObject(obj, self.objects_central_widget, font_manager=self.font_manager,
                                        hide_func=self.object_hidden, select_func=self.select_object)
            self.objects_layout.addWidget(ib_obj)
            self.objects.append(ib_obj)

    def select_object(self, obj_index):
        for obj in self.objects:
            obj.select(revert=True)
        if obj_index is not None:
            if isinstance(obj_index, tuple):
                if obj_index[1] < len(self.objects):
                    self.objects[obj_index[1]].select()
            elif isinstance(obj_index, InspectorBarObject):
                if self.change_current_object:
                    self.change_current_object(obj_index.obj.id)

    def clear_layout(self):
        for i in range(self.objects_layout.count() - 1, -1, -1):
            self.objects_layout.itemAt(i).widget().deleteLater()

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.bg_style_sheet)
