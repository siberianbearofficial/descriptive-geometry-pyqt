from PyQt5.QtWidgets import QVBoxLayout
from utils.ui.widgets.widget import Widget
from utils.drawing.plot import Plot
from utils.color import *


class PlotBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.setStyleSheet(f"background-color: {WHITE_COLOR}; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.painter_widget = Plot(self.central_widget)
        self.layout.addWidget(self.painter_widget)
