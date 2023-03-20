from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from utils.render.render_plot import RenderPlot
from utils.ui.windows.options_window import OptionsWidget


class RenderWindow(QMainWindow):
    def __init__(self):
        super(RenderWindow, self).__init__()
        self.setWindowTitle("DescriptiveGeometry - Render")
        self.strange_widget = QWidget()
        self.setCentralWidget(self.strange_widget)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scale_list = [15, 9, 6, 3, 3/2, 3/3, 3/5]
        self.options_widget = OptionsWidget(
            {
                'Format:': {'type': 'combo', 'values': ['A4']},
                'Scale:': {'type': 'combo', 'values': ['5:1', '3:1', '2:1', '1:1', '1:2', '1:3', '1:5'],
                           'initial': 3, 'max_visible': 7},
                'File:': {'type': 'file', 'initial': 'image.png', 'filter': 'Picture: (*.png)', 'save': True},
                'Render': {'type': 'button', 'text': 'Render'}
            })
        self.options_widget.clicked.connect(self.triggered)
        layout.addWidget(self.options_widget)

        self.plot = RenderPlot(861, 600)
        self.plot.setStyleSheet("border: 2px solid #00ABB3;")
        layout.addWidget(self.plot)

        self.strange_widget.setLayout(layout)

    def triggered(self, key):
        if key == 'Render':
            self.plot.save_image(self.options_widget['File:'])
            self.hide()
        elif key == 'Scale:':
            self.plot.set_zoom(self.scale_list[self.options_widget['Scale:']])
