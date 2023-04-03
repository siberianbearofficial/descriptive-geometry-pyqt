from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from utils.ui.widgets.widget import Widget
from utils.ui.bars.inspector_bar_object import InspectorBarObject
from utils.color import *


class InspectorBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.font_manager = font_manager

        self.setStyleSheet(f"background-color: {LIGHT_COLOR}; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)

        self.object_hidden = None
        self.change_current_object = None

        self.objects = list()

        # for i in range(3):
        #     obj = InspectorBarObject(self.central_widget, font_manager=font_manager)
        #     self.layout.addWidget(obj)

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
            ib_obj = InspectorBarObject(obj, self.central_widget, font_manager=self.font_manager,
                                        hide_func=self.object_hidden, select_func=self.select_object)
            self.layout.addWidget(ib_obj)
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
        for i in range(self.layout.count() - 1, -1, -1):
            self.layout.itemAt(i).widget().deleteLater()
