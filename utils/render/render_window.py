from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from utils.render.render_plot import RenderPlot
from utils.ui.windows.options_window import OptionsWidget

render_params = {'A4': 1, 'A3': 2 ** 0.5, 'A2': 2}
formats = ['A2', 'A3', 'A4']
zoom = [15, 9, 6, 3, 1.5, 1, 0.6]
zoom_str = ['5:1', '3:1', '2:1', '1:1', '1:2', '1:3', '1:5']


class RenderWindow(QMainWindow):
    def __init__(self):
        super(RenderWindow, self).__init__()
        self.setWindowTitle("DescriptiveGeometry - Render")
        self.strange_widget = QWidget()
        self.setCentralWidget(self.strange_widget)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.options_widget = OptionsWidget(
            {
                'Format:': {'type': 'combo', 'values': formats, 'initial': formats.index('A4')},
                'Scale:': {'type': 'combo', 'values': zoom_str, 'initial': zoom_str.index('1:1'), 'max_visible': 7},
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
            self.plot.save_image(
                self.options_widget['File:'], 6 * render_params[formats[self.options_widget['Format:']]], 3)
            self.hide()
        elif key == 'Scale:' or key == 'Format:':
            self.plot.set_zoom(1 / render_params[formats[self.options_widget['Format:']]] *
                               zoom[self.options_widget['Scale:']])
            self.plot.reset_labels()
