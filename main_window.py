from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from utils.drawing.Plot2 import PlotBar
from DrawBar import DrawBar
from CmdBar import CmdBar
from PropertiesBar import PropertiesBar
from InspectorBar import InspectorBar
from ToolBar import ToolBar
from MenuBar import MenuBar
from layer_window import LayerWindow
from utils.drawing.object_manager import ObjectManager
from utils.drawing.history import HistoryManager
from column import Column

import utils.history.serializer as srl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DescriptiveGeometry')
        self.setMinimumSize(1080, 740)

        central_widget = QWidget(self)
        central_widget.setStyleSheet("background-color: #3C4048;")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        left_column = Column()
        middle_column = Column()
        right_column = Column()

        # Plot
        self.plot_bar = PlotBar(middle_column)
        self.plot = self.plot_bar.painter_widget
        self.hm = HistoryManager(self.plot)
        self.object_manager = ObjectManager(
            self.plot.update, self.plot.modify_plot_object, self.plot.update_plot_objects, self.hm.add_record,
            (self.plot.set_selected_object,))
        self.plot.add_object_func = self.object_manager.add_object
        self.plot.objectSelected.connect(self.object_manager.select_object)

        # Draw bar
        draw_tools_names = ['Point', 'Segment', 'Line', 'Plane', 'Cylinder', 'PerpL', 'Plane3p', 'Spline', 'RS', 'Horizontal']
        self.draw_bar = DrawBar(left_column, *draw_tools_names).set_on_click_listeners(
            *[
                lambda: self.plot.draw('point'),
                lambda: self.plot.draw('segment'),
                lambda: self.plot.draw('line'),
                lambda: self.plot.draw('plane'),
                lambda: self.plot.draw('cylinder'),
                lambda: self.plot.draw('perpendicular_line'),
                lambda: self.plot.draw('plane_3p'),
                lambda: self.plot.draw('spline'),
                lambda: self.plot.draw('rotation_surface'),
                lambda: self.plot.draw('horizontal')
            ]
        )

        # Cmd bar
        self.cmd_bar = CmdBar(middle_column)
        self.cmd_bar.add_object = self.plot.add_object
        self.cmd_bar.clear_plot = self.plot.clear
        self.plot.printToCommandLine.connect(self.cmd_bar.set_text)

        # Toolbar
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

        self.tool_bar = ToolBar(right_column, *[tool_info['name'] for tool_info in tools_info]).set_images(
            *[tool_info['image'] for tool_info in tools_info]).set_on_click_listeners(
            *[tool_info['func'] for tool_info in tools_info])

        # Properties bar
        self.properties_bar = PropertiesBar(right_column)
        self.plot.show_object_properties = self.properties_bar.open_object
        self.properties_bar.save = self.plot.save_object_properties

        # Inspector bar
        self.inspector_bar = InspectorBar(right_column)

        # Layer window
        # self.layer_window = LayerWindow(self.plot.layers, self.plot.current_layer)
        # self.layer_window.selectLayer.connect(self.plot.set_current_layer)
        # self.layer_window.addLayer.connect(lambda: (self.plot.add_layer(), self.layer_window.update_layer_list(
        #     self.plot.layers, self.plot.current_layer)))
        # self.layer_window.setLayerHidden.connect(lambda ind, flag: self.plot.layers[ind].set_hidden(flag))
        # self.layer_window.removeLayer.connect(self.plot.delete_layer)

        # self.plot.layersModified.connect(self.layer_window.update_layer_list)
        # self.layer_window = LayerWindow(self.plot.layers, self.plot.current_layer)
        # self.layer_window.selectLayer.connect(self.plot.set_current_layer)
        # self.layer_window.addLayer.connect(lambda: (self.plot.add_layer(), self.layer_window.update_layer_list(
        #     self.plot.layers, self.plot.current_layer)))
        # self.layer_window.setLayerHidden.connect(lambda ind, flag: self.plot.layers[ind].set_hidden(flag))
        # self.layer_window.removeLayer.connect(self.plot.delete_layer)
        # self.plot.layersModified.connect(self.layer_window.update_layer_list)
        # self.plot.setCmdStatus.connect(self.cmd_bar.set_command_to_plot)

        # Menubar
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
                        'Delete': (self.object_manager.delete_selected_object, 'Alt+Delete'),
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
                'Hide props': (self.properties_bar.hide, None),
                'Show props': (self.properties_bar.show, None),
            }
        )
        self.setMenuBar(self.menu_bar)

        left_column.add(self.draw_bar)
        middle_column.add(self.plot_bar, 10).add(self.cmd_bar, 1)
        right_column.add(self.tool_bar, 2).add(self.properties_bar, 6).add(self.inspector_bar, 5)

        main_layout.addWidget(left_column, 2)
        main_layout.addWidget(middle_column, 8)
        main_layout.addWidget(right_column, 2)

        self.setCentralWidget(central_widget)

    def keyPressEvent(self, a0) -> None:
        # if a0.key() == Qt.Key_Escape:
        #     self.object_manager.delete_selected_object()
        self.plot.keyPressEvent(a0)

    def serialize(self):
        srl.serialize(self.plot.serialize())

    def deserialize(self):
        self.plot.deserialize(srl.deserialize())
        self.layer_window.update_layer_list(self.plot.layers, self.plot.current_layer)


import resources_rc
