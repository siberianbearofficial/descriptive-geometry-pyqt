from PyQt5.QtWidgets import QVBoxLayout
from utils.ui.widgets.widget import Widget
from utils.drawing.plot import Plot


class PlotBar(Widget):
    def __init__(self, parent, font_manager):
        super().__init__(parent)

        self.setStyleSheet("background-color: #ffffff; border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.painter_widget = Plot(self.central_widget)
        self.layout.addWidget(self.painter_widget)
