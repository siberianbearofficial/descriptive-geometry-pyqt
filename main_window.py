from PyQt5.QtWidgets import QMainWindow, QWidget
from utils.drawing.Plot2 import Plot
from DrawBar import DrawBar
from CmdBar import CmdBar
from PropertiesBar import PropertiesBar
from InspectorBar import InspectorBar
from ToolBar import ToolBar
from MenuBar import MenuBar
from layer_window import LayerWindow

import utils.history.serializer as srl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DescriptiveGeometry')
        self.setFixedSize(1080, 740)

        self.centralwidget = QWidget(self)
        self.centralwidget.setStyleSheet("background-color: #3C4048;")

        self.plot = Plot(self.centralwidget)

        draw_tools_names = ['Point', 'Segment', 'Line', 'Plane', 'Cylinder', 'PerpL', 'Plane3p', 'Spline', 'RS']
        self.draw_bar = DrawBar(self.centralwidget, *draw_tools_names).set_on_click_listeners(
            *[
                lambda: self.plot.draw('point'),
                lambda: self.plot.draw('segment'),
                lambda: self.plot.draw('line'),
                lambda: self.plot.draw('plane'),
                lambda: self.plot.draw('cylinder'),
                lambda: self.plot.draw('perpendicular_line'),
                lambda: self.plot.draw('plane_3p'),
                lambda: self.plot.draw('spline'),
                lambda: self.plot.draw('rotation_surface')
            ]
        )

        self.cmd_bar = CmdBar(self.centralwidget).set_plot(self.plot)

        self.plot.printToCommandLine.connect(self.cmd_bar.set_text)

        tools_info = [
            {
                'name': 'Ruler',
                'image': 'ruler_icon.png',
                'func': lambda: self.plot.draw('distance'),
            },
            {
                'name': 'Angle',
                'image': 'angle_icon.png',
                'func': lambda: self.plot.draw('angle'),
            },
            {
                'name': 'Intersection',
                'image': 'intersection_icon.png',
                'func': lambda: self.plot.draw('intersection'),
            },
        ]

        self.tool_bar = ToolBar(self.centralwidget, *[tool_info['name'] for tool_info in tools_info]).set_images(
            *[tool_info['image'] for tool_info in tools_info]).set_on_click_listeners(
            *[tool_info['func'] for tool_info in tools_info])

        self.properties_bar = PropertiesBar(self.centralwidget)
        self.plot.show_object_properties = self.properties_bar.open
        self.properties_bar.save = self.plot.save_object_properties

        self.inspector_bar = InspectorBar(self.centralwidget)
        self.layer_window = LayerWindow(self.plot.layers, self.plot.current_layer)
        self.layer_window.selectLayer.connect(self.plot.set_current_layer)
        self.layer_window.addLayer.connect(lambda: (self.plot.add_layer(), self.layer_window.update_layer_list(
            self.plot.layers, self.plot.current_layer)))
        self.layer_window.setLayerHidden.connect(lambda ind, flag: self.plot.layers[ind].set_hidden(flag))
        self.layer_window.removeLayer.connect(self.plot.delete_layer)
        self.plot.layersModified.connect(self.layer_window.update_layer_list)

        self.menu_bar = MenuBar(
            {
                'File':
                    {
                        'Save': (self.serialize, 'Ctrl+S'),
                        'Load': (self.deserialize, 'Ctrl+Alt+Y'),
                    },
                'Edit':
                    {
                        'Undo': (lambda: self.plot.hm.undo(), 'Alt+Z'),
                        'Redo': (lambda: self.plot.hm.undo(redo=True), 'Alt+Shift+Z'),
                        'Delete': (self.plot.delete_selected, None),
                        'Copy': (lambda: print('copy'), 'Ctrl+C'),
                        'Paste': (lambda: print('paste'), 'Ctrl+V'),
                    },
                'Draw':
                    {
                        'Point': (lambda: self.plot.draw('point'), 'Alt+P'),
                        'Segment': (lambda: self.plot.draw('segment'), 'Alt+S'),
                        'Line': (lambda: self.plot.draw('line'), 'Alt+L'),
                        'Plane': (lambda: self.plot.draw('plane'), None),
                        'Cylinder': (lambda: self.plot.draw('cylinder'), 'Shift+Alt+P'),
                        'PerpL': (lambda: self.plot.draw('perpendicular_line'), None),
                        'Plane3p': (lambda: self.plot.draw('plane_3p'), 'Shift+Alt+P'),
                    },
                'Layers': (lambda: self.layer_window.show(), 'Ctrl+L'),
            }
        )
        self.setMenuBar(self.menu_bar)

        self.setCentralWidget(self.centralwidget)

    def keyPressEvent(self, a0) -> None:
        self.plot.keyPressEvent(a0)

    def serialize(self):
        srl.serialize(self.plot.serialize())

    def deserialize(self):
        self.plot.deserialize(srl.deserialize())
        self.layer_window.update_layer_list(self.plot.layers, self.plot.current_layer)


import resources_rc
