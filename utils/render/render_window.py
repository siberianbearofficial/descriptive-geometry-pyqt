from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QPushButton
from utils.render.render_plot import RenderPlot, ChooseAreaPlot, FinalEditPlot
from utils.ui.windows.options_window import OptionsWidget
from utils.color import *

render_params = {'A4': 1, 'A3': 2 ** 0.5, 'A2': 2}
formats = ['A2', 'A3', 'A4']
zoom = [15, 9, 6, 3, 1.5, 1, 0.6]
zoom_str = ['5:1', '3:1', '2:1', '1:1', '1:2', '1:3', '1:5']


class RenderWindow(QMainWindow):
    def __init__(self):
        super(RenderWindow, self).__init__()
        self.setWindowTitle("DescriptiveGeometry - Render")    # TODO: remove constant app title
        self.strange_widget = QWidget()
        self.setCentralWidget(self.strange_widget)
        self.stage = 0
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.options_widget = OptionsWidget(
            {
                'Format:': {'type': 'combo', 'values': formats, 'initial': formats.index('A4')},
                'Scale:': {'type': 'combo', 'values': zoom_str, 'initial': zoom_str.index('1:1'), 'max_visible': 7},
                'File:': {'type': 'file', 'initial': 'image.png', 'filter': 'Picture: (*.png)', 'save': True}
            })
        self.options_widget.clicked.connect(self.triggered)
        layout.addWidget(self.options_widget)

        self.plot1 = ChooseAreaPlot(861, 600)
        self.plot1.setStyleSheet(f"border: 2px solid {ACCENT_COLOR};")
        layout.addWidget(self.plot1)

        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        self.button_back = QPushButton("Back")
        buttons_layout.addWidget(self.button_back)

        self.button_next = QPushButton("Next")
        buttons_layout.addWidget(self.button_next)

        self.strange_widget.setLayout(layout)

    def button_next(self, *args):
        if self.stage == 0:                     # TODO: Memory
            self.open_second_stage()
            self.stage = 1
        elif self.stage == 1:
            self.plot2.save_image(
                self.options_widget['File:'], 6 * render_params[formats[self.options_widget['Format:']]], 3)

    def open_second_stage(self):
        self.plot1.hide()
        self.plot2 = FinalEditPlot(self.plot1.width(), self.plot1.height())

    def triggered(self, key):
        if key == 'Scale:' or key == 'Format:':
            self.plot1.set_zoom(1 / render_params[formats[self.options_widget['Format:']]] *
                               zoom[self.options_widget['Scale:']])
            self.plot1.reset_labels()
