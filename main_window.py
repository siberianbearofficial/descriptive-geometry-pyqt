from PyQt5.QtWidgets import QMainWindow, QWidget
from utils.drawing.Plot2 import Plot
from DrawBar import DrawBar
from CmdBar import CmdBar
from PropertiesBar import PropertiesBar
from InspectorBar import InspectorBar
from ToolBar import ToolBar
from MenuBar import MenuBar

import utils.history.serializer as srl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DescriptiveGeometry')
        self.setFixedSize(1080, 740)

        self.centralwidget = QWidget(self)
        self.centralwidget.setStyleSheet("background-color: #3C4048;")

        self.plot = Plot(self.centralwidget)

        draw_tools_names = ['Point', 'Segment', 'Line', 'Plane', 'Cylinder', 'PerpL', 'Plane3p']
        self.draw_bar = DrawBar(self.centralwidget, *draw_tools_names).set_on_click_listeners(
            *[
                lambda: self.plot.draw('point'),
                lambda: self.plot.draw('segment'),
                lambda: self.plot.draw('line'),
                lambda: self.plot.draw('plane'),
                lambda: self.plot.draw('cylinder'),
                lambda: self.plot.draw('perpendicular_line'),
                lambda: self.plot.draw('plane_3p'),
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
        self.inspector_bar = InspectorBar(self.centralwidget)

        self.menu_bar = MenuBar('Delete', 'Save', 'Load').connect(self.plot.delete_selected, self.serialize,
                                                                  self.deserialize)
        self.setMenuBar(self.menu_bar)

        self.setCentralWidget(self.centralwidget)

    def keyPressEvent(self, a0) -> None:
        self.plot.keyPressEvent(a0)

    def serialize(self):
        srl.serialize(self.plot.serialize())

    def deserialize(self):
        self.plot.deserialize(srl.deserialize())


import resources_rc
