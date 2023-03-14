from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from utils.ui.widgets.widget import Widget
from utils.ui.bars.inspector_bar_object import InspectorBarObject


class InspectorBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.setStyleSheet("background-color: #EAEAEA; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)

        for i in range(3):
            obj = InspectorBarObject(self.central_widget, font_manager=font_manager)
            self.layout.addWidget(obj)
