from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox

from utils.render.render_window import RenderWindow
from utils.ui.bars.plot_bar import PlotBar
from utils.ui.bars.draw_bar import DrawBar
from utils.ui.bars.cmd_bar import CmdBar
from utils.ui.bars.properties_bar import PropertiesBar
from utils.ui.bars.inspector_bar import InspectorBar
from utils.ui.bars.tool_bar import ToolBar
from utils.ui.bars.menu_bar import MenuBar
from utils.objects.object_manager import ObjectManager
from utils.ui.themes.theme_manager import ThemeManager
from utils.ui.widgets.column import Column
from utils.fonts.font_manager import FontManager
from utils.history.settings_manager import SettingsManager
from utils.ui.windows.layer_window import LayerWindow

from utils.history.serializer import Serializer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1180, 740)

        fm = FontManager()
        self.srl = Serializer()
        self.settings_manager = SettingsManager(self.srl)
        self.srl.recent_directory = self.settings_manager.recent_directory
        self.tm = ThemeManager(self.srl)
        # self.tm.load_theme('Basic')

        self.setWindowTitle('DescriptiveGeometry')

        central_widget = QWidget(self)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        left_column = Column()
        left_column.setFixedWidth(200)

        middle_column = Column()

        right_column = Column()
        right_column.setFixedWidth(250)

        # Plot
        self.plot_bar = PlotBar(middle_column, font_manager=fm, theme_manager=self.tm)
        self.plot = self.plot_bar.painter_widget

        # Properties bar
        self.properties_bar = PropertiesBar(right_column, font_manager=fm, theme_manager=self.tm)
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
                'Point': {
                    'Point': (lambda: self.plot.draw('point'),),
                },
                'Segment': {
                    'Segment': (lambda: self.plot.draw('segment'),),
                },
                'Line': {
                    'Line': (lambda: self.plot.draw('line'),),
                    'Perp': (lambda: self.plot.draw('perpendicular_line'),),
                    'Horizontal': (lambda: self.plot.draw('horizontal'),),
                },
                'Plane': {
                    'Plane': (lambda: self.plot.draw('plane'),),
                    'Plane 3P': (lambda: self.plot.draw('plane_3p'),),
                },
                'Spline': {
                    'Spline': (lambda: self.plot.draw('spline'),),
                },
                'Rotation Surface': {
                    'Rot Surf': (lambda: self.plot.draw('rotation_surface'),),
                    'Cylinder': (lambda: self.plot.draw('cylinder'),),
                    'Cone': (lambda: self.plot.draw('cone'),),
                    'Sphere': (lambda: self.plot.draw('sphere'),),
                },
            }, parent=left_column, font_manager=fm, theme_manager=self.tm)

        # Cmd bar
        self.cmd_bar = CmdBar(middle_column, font_manager=fm, theme_manager=self.tm)
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
            }, parent=right_column, font_manager=fm, theme_manager=self.tm)
        self.tool_bar.setFixedHeight(120)

        # Inspector bar
        self.inspector_bar = InspectorBar(right_column, font_manager=fm, theme_manager=self.tm)
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
                                str(i): (self.get_recent_lambda(i), None) for i in range(8)
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
            },
            theme_manager=self.tm)
        self.setMenuBar(self.menu_bar)

        self.update_recent_files_menu()

        left_column.add(self.draw_bar)
        middle_column.add(self.plot_bar).add(self.cmd_bar)
        right_column.add(self.tool_bar).add(self.properties_bar).add(self.inspector_bar)

        main_layout.addWidget(left_column)
        main_layout.addWidget(middle_column)
        main_layout.addWidget(right_column)

        self.setCentralWidget(central_widget)

        self.set_styles()

    def get_recent_lambda(self, i):
        return lambda: self.deserialize(i)

    def keyPressEvent(self, a0) -> None:
        self.plot.keyPressEvent(a0)

    def serialize(self, create_new=False):
        """
        Function that opens and deserializes chosen file
        :param create_new: current file is used if False else QFileDialog is opened
        :return:
        """

        try:
            path = self.srl.serialize_file(self, create_new, self.object_manager.serialize())
        except Exception as e:
            print('Exception in MainWindow (serialize func):', e)
        else:
            self.settings_manager.add_to_recent_files(path)  # TODO: do something with settings manager!
            self.update_recent_files_menu()
            self.settings_manager.set_recent_directory(path)

    def deserialize(self, path=None) -> None:
        """
        Function that opens and deserializes chosen file
        :param path: path to the file or index of recent file
        :return:
        """

        if isinstance(path, int):
            path = self.menu_bar.action_dict['File']['Recent files'].get(str(path), None)
            if path:
                path = path.text()

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
        self.render_window.plot1.update_plot_objects(self.object_manager.get_all_objects())
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

    def set_styles(self):
        self.setStyleSheet(self.tm.get_style_sheet(self.__class__.__name__))
        self.cmd_bar.set_styles()
        self.draw_bar.set_styles()
        self.inspector_bar.set_styles()
        self.plot_bar.set_styles()
        self.properties_bar.set_styles()
        self.tool_bar.set_styles()
        self.menu_bar.set_styles()

    def closeEvent(self, a0) -> None:
        self.settings_manager.serialize()
        super(MainWindow, self).closeEvent(a0)


import resources_rc
