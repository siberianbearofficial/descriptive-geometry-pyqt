import copy

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFileDialog, QMessageBox, QPushButton

from utils.render.render_window import RenderWindow
from utils.ui.bars.plot_bar import PlotBar
from utils.ui.bars.draw_bar import DrawBar
from utils.ui.bars.cmd_bar import CmdBar
from utils.ui.bars.properties_bar import PropertiesBar
from utils.ui.bars.inspector_bar import InspectorBar
from utils.ui.bars.tool_bar import ToolBar
from utils.ui.bars.menu_bar import MenuBar
from utils.objects.object_manager import ObjectManager
from utils.ui.widgets.column import Column
from utils.fonts.font_manager import FontManager
from utils.history.settings_manager import SettingsManager
from utils.ui.windows.layer_window import LayerWindow
from utils.color import *

import os

from utils.history.serializer import Serializer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1180, 740)

        fm = FontManager()
        self.srl = Serializer()
        self.settings_manager = SettingsManager(self.srl)
        self.srl.recent_directory = self.settings_manager.recent_directory

        self.setWindowTitle('DescriptiveGeometry')

        central_widget = QWidget(self)
        central_widget.setStyleSheet(f"background-color: {DARK_COLOR};")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        left_column = Column()
        left_column.setFixedWidth(200)

        middle_column = Column()

        right_column = Column()
        right_column.setFixedWidth(250)

        # Plot
        self.plot_bar = PlotBar(middle_column, font_manager=fm)
        self.plot = self.plot_bar.painter_widget

        # Properties bar
        self.properties_bar = PropertiesBar(right_column, font_manager=fm)
        # self.properties_bar.save = self.plot.save_object_properties
        self.properties_bar.setMinimumHeight(150)

        # Object manager
        self.object_manager = ObjectManager(
            self.plot.update, self.plot.modify_plot_object, self.plot.update_plot_objects,
            (self.plot.set_selected_object, self.properties_bar.open_object))
        self.plot.add_object_func = self.object_manager.add_object
        self.plot.objectSelected.connect(self.object_manager.select_object)

        self.properties_bar.set_obj_name_func(self.object_manager.set_object_name)
        self.properties_bar.set_obj_color_func(self.object_manager.set_object_color)
        self.properties_bar.set_obj_thickness_func(self.object_manager.set_object_thickness)
        self.properties_bar.set_layers_list(self.object_manager.layers)
        self.properties_bar.set_obj_ag_object_func(self.object_manager.set_object_ag_obj)
        self.properties_bar.set_obj_layer_func(self.object_manager.set_object_layer)
        self.properties_bar.update_layers_widget()
        self.properties_bar.hide()

        # Draw bar
        self.draw_bar = DrawBar(
            {
                'Point': (lambda: self.plot.draw('point'),),
                'Segment': (lambda: self.plot.draw('segment'),),
                'Line': (lambda: self.plot.draw('line'),),
                'Plane': (lambda: self.plot.draw('plane'),),
                'Cylinder': (lambda: self.plot.draw('cylinder'),),
                'Perp': (lambda: self.plot.draw('perpendicular_line'),),
                'Plane 3 points': (lambda: self.plot.draw('plane_3p'),),
                'Spline': (lambda: self.plot.draw('spline'),),
                'Rotation Surface': (lambda: self.plot.draw('rotation_surface'),),
                'Horizontal': (lambda: self.plot.draw('horizontal'),),
            }, parent=left_column, font_manager=fm)

        # Cmd bar
        self.cmd_bar = CmdBar(middle_column, font_manager=fm)
        self.cmd_bar.setFixedHeight(80)
        self.cmd_bar.add_object = self.plot.add_object
        self.cmd_bar.clear_plot = self.plot.clear
        self.plot.printToCommandLine.connect(self.cmd_bar.set_text)

        # Toolbar
        self.tool_bar = ToolBar(
            {
                'Ruler': (lambda: self.plot.draw('distance'), 'ruler_icon.png'),
                'Angle': (lambda: self.plot.draw('angle'), 'angle_icon.png'),
                'Intersection': (lambda: self.plot.draw('intersection'), 'intersection_icon.png')
            }, parent=right_column, font_manager=fm)
        self.tool_bar.setFixedHeight(120)

        # Inspector bar
        self.inspector_bar = InspectorBar(right_column, font_manager=fm)
        self.inspector_bar.setMinimumHeight(100)
        self.inspector_bar.set_object_hidden_func(self.object_manager.set_object_hidden)
        self.inspector_bar.set_change_current_object_func(self.object_manager.select_object)
        self.object_manager.objects_changed = self.inspector_bar.set_objects
        self.object_manager.current_object_changed = self.inspector_bar.select_object

        # Render window
        self.render_window = RenderWindow()

        # Layer window
        self.layer_window = LayerWindow(
            self.object_manager.add_layer,
            self.object_manager.delete_layer,
            self.object_manager.select_layer,
            lambda *args: self.object_manager.set_layer_attr('name', *args),
            self.object_manager.set_layer_hidden,
            lambda *args: self.object_manager.set_layer_attr('color', *args),
            lambda *args: self.object_manager.set_layer_attr('thickness', *args)
        )
        self.layer_window.update_layer_list(self.object_manager.layers, self.object_manager.current_layer)
        self.object_manager.set_layers_func(
            (self.layer_window.add_layer, self.properties_bar.update_layers_widget),
            (self.layer_window.delete_layer, self.properties_bar.update_layers_widget), (self.layer_window.hide_layer,),
            (self.layer_window.select_layer,),
            (self.layer_window.rename_layer, self.properties_bar.update_layers_widget),
            (self.layer_window.set_layer_color,),
            (self.layer_window.set_layer_thickness,),
            self.layer_window.update_layer_list,
        )
        self.plot.setCmdStatus.connect(self.cmd_bar.set_command_to_plot)

        # Menubar
        self.menu_bar = MenuBar(
            {
                'File':
                    {
                        'New': (lambda: self.new_file(), 'Ctrl+Alt+T'),
                        'Open': (lambda: self.deserialize(), 'Ctrl+Alt+Y'),
                        'Save': (self.serialize, 'Ctrl+S'),
                        'Save as': (lambda: self.serialize(True), 'Ctrl+Shift+S'),
                        'Recent files':
                            {
                                '0': (lambda: self.deserialize(self.settings_manager.recent_file(0)), None),
                                '1': (lambda: self.deserialize(self.settings_manager.recent_file(1)), None),
                                '2': (lambda: self.deserialize(self.settings_manager.recent_file(2)), None),
                                '3': (lambda: self.deserialize(self.settings_manager.recent_file(3)), None),
                                '4': (lambda: self.deserialize(self.settings_manager.recent_file(4)), None),
                                '5': (lambda: self.deserialize(self.settings_manager.recent_file(5)), None),
                                '6': (lambda: self.deserialize(self.settings_manager.recent_file(6)), None),
                                '7': (lambda: self.deserialize(self.settings_manager.recent_file(7)), None)
                                # '1': (lambda: self.deserialize(1), None),
                                # '2': (lambda: self.deserialize(2), None),
                                # '3': (lambda: self.deserialize(3), None),
                                # '4': (lambda: self.deserialize(4), None),
                                # '5': (lambda: self.deserialize(5), None),
                                # '6': (lambda: self.deserialize(6), None),
                                # '7': (lambda: self.deserialize(7), None)
                            },
                    },
                'Edit':
                    {
                        'Undo': (lambda: self.object_manager.hm.undo(), 'Alt+Z'),
                        'Redo': (lambda: self.object_manager.hm.undo(redo=True), 'Alt+Shift+Z'),
                        'Delete': (lambda: self.object_manager.delete_object(), 'Alt+Delete'),
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
                'Layers': (self.layer_window.show, 'Ctrl+L'),
                'Render': (self.start_render, None)
            }
        )
        self.setMenuBar(self.menu_bar)

        self.update_recent_files_menu()

        left_column.add(self.draw_bar)
        middle_column.add(self.plot_bar).add(self.cmd_bar)
        right_column.add(self.tool_bar).add(self.properties_bar).add(self.inspector_bar)

        main_layout.addWidget(left_column)
        main_layout.addWidget(middle_column)
        main_layout.addWidget(right_column)

        self.setCentralWidget(central_widget)

    def keyPressEvent(self, a0) -> None:
        self.plot.keyPressEvent(a0)

    def serialize(self, create_new=False):
        """
        Function that opens and deserializes chosen file
        :param create_new: current file is used if True else QFileDialog is opened
        :return:
        """

        try:
            path = self.srl.serialize_file(self, create_new, self.object_manager.serialize())
        except Exception as e:
            print(e)
        else:
            self.settings_manager.add_to_recent_files(path)  # TODO: do something with settings manager!
            self.update_recent_files_menu()
            self.settings_manager.set_recent_directory(path)

    def deserialize(self, path: str = None) -> None:
        """
        Function that opens and deserializes chosen file
        :param path: path to the file
        :return:
        """

        try:
            self.srl.deserialize_file(self, path, self.object_manager.deserialize)
        except FileNotFoundError:
            pass
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Unknown error", str(e))
        else:
            self.settings_manager.add_to_recent_files(path)  # TODO: do something with settings manager!
            self.update_recent_files_menu()
            self.settings_manager.set_recent_directory(path)

            self.update_objects()

    def update_objects(self):
        self.layer_window.update_layer_list(self.object_manager.layers, self.object_manager.current_layer)
        self.properties_bar.update_layers_widget()
        self.plot.update()

    def new_file(self):
        self.object_manager.clear()
        self.srl.new_file()
        self.plot.update()

    def start_render(self):
        self.render_window.plot.update_plot_objects(self.object_manager.get_all_objects())
        self.render_window.show()

    def update_recent_files_menu(self):
        """
        Function that updates recent files menu.
        :return:
        """

        i = -1
        for i, path in enumerate(self.settings_manager.recent_files):
            self.menu_bar.action_dict['File']['Recent files'][str(i)].setText(path)
        for i in range(i + 1, 8):
            self.menu_bar.action_dict['File']['Recent files'][str(i)].setText('')

    def closeEvent(self, a0) -> None:
        self.settings_manager.serialize()
        super(MainWindow, self).closeEvent(a0)


import resources_rc


class Test(QWidget):
    def __init__(self):
        super().__init__()

        self.d = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

        layout = QHBoxLayout(self)
        btn = QPushButton('Open')
        btn.clicked.connect(self.filename)
        layout.addWidget(btn)

    def filename(self):
        self.path = QFileDialog.getOpenFileName(self, 'Open File', self.d)[0]
        print(self.path)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    widget = Test()
    widget.show()
    app.exec()
