from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from utils.ui.widgets.widget import Widget
from utils.ui.bars.inspector_bar_object import InspectorBarObject


class InspectorBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.font_manager = font_manager

        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)

        self.objects_changed = None

        # for i in range(3):
        #     obj = InspectorBarObject(self.central_widget, font_manager=font_manager)
        #     self.layout.addWidget(obj)

    def set_objects_changed_func(self, func):
        if func:
            self.objects_changed = func
        return self

    def set_objects(self, objects):
        self.clear_layout()
        for obj in objects:
            self.layout.addWidget(InspectorBarObject(obj.name, self.central_widget, font_manager=self.font_manager))

    def clear_layout(self):
        for i in range(self.layout.count() - 1, -1, -1):
            self.layout.itemAt(i).widget().deleteLater()
