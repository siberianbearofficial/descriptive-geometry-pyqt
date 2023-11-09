from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QVBoxLayout

from utils.drawing.drawing_on_plot import Drawer
from utils.drawing.plot import Plot
from utils.fonts.font_manager import FontManager
from utils.history.serializer import Serializer
from utils.history.settings_manager import SettingsManager
from utils.objects.object_manager import ObjectManager
from utils.ui.bars.draw_bar import DrawBar
from utils.ui.bars.menu_bar import MenuBar
from utils.ui.bars.properties_bar import PropertiesBar
from utils.ui.bars.top_bar import TopBar
from utils.ui.themes.theme_manager import ThemeManager
from utils.ui.windows.layer_window import LayerWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1180, 740)

        fm = FontManager()
        self.srl = Serializer()
        self.settings_manager = SettingsManager(self.srl)
        self.srl.recent_directory = self.settings_manager.recent_directory
        self.tm = ThemeManager('dark')
        # self.tm.load_theme('Basic')

        self.setWindowTitle('DescriptiveGeometry')

        # Object manager
        self.object_manager = ObjectManager(self.tm)

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.top_bar = TopBar(self.tm, self.object_manager)
        main_layout.addWidget(self.top_bar)

        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(0)

        middle_column = QVBoxLayout()
        right_column = QVBoxLayout()

        # Plot
        self.plot = Plot(self.tm, self.object_manager)
        self.top_bar.intersectionClicked.connect(lambda: self.plot.draw(Drawer.INTERSECTION))
        self.top_bar.inversionChanged.connect(self.plot.set_inversion)

        # Properties bar
        self.properties_bar = PropertiesBar(self.tm, self.object_manager)
        self.properties_bar.setParent(self.plot)
        self.properties_bar.move(5, 5)
        self.properties_bar.hide()

        # Layer window

        self.layer_window = LayerWindow(self.tm, self.object_manager)

        # Draw bar
        self.draw_bar = DrawBar(
            {
                'Point': {
                    'Точка': ('point', lambda: self.plot.draw(Drawer.POINT),),
                },
                'Segment': {
                    'Отрезок': ('segment', lambda: self.plot.draw(Drawer.SEGMENT),),
                },
                'Line': {
                    'Прямая': ('line', lambda: self.plot.draw(Drawer.LINE),),
                    'Перпендикуляр': ('perpendicular', lambda: self.plot.draw(Drawer.PERPENDICULAR_LINE),),
                    'Параллельно': ('parallel', lambda: self.plot.draw('perpendicular_line'),),
                    'Горизонталь': ('horizontal', lambda: self.plot.draw('horizontal'),),
                    'Фронталь': ('frontal', lambda: self.plot.draw('horizontal'),),
                },
                'Плоскость': {
                    'Плоскость': ('plane', lambda: self.plot.draw(Drawer.PLANE),),
                    'По трем точкам': ('plane_3p', lambda: self.plot.draw(Drawer.PLANE_3P),),
                },
                'Spline': {
                    'Сплайн': ('point', lambda: self.plot.draw('spline'),),
                },
                'Поверхность вращения': {
                    'Поверхность вращения': ('rotation_surface', lambda: self.plot.draw('rotation_surface'),),
                    'Цилиндр': ('cylinder', lambda: self.plot.draw(Drawer.CYLINDER),),
                    'Конус': ('cone', lambda: self.plot.draw(Drawer.CONE),),
                    'Сфера': ('sphere', lambda: self.plot.draw(Drawer.SPHERE),),
                    'Тор': ('tor', lambda: self.plot.draw(Drawer.TOR),),
                },
            }, theme_manager=self.tm)

        # Cmd bar
        # self.cmd_bar = CmdBar(middle_column, font_manager=fm, theme_manager=self.tm)
        # self.cmd_bar.setFixedHeight(80)
        # self.cmd_bar.add_object = self.plot.add_object
        # self.cmd_bar.clear_plot = self.plot.clear
        # self.plot.printToCommandLine.connect(self.cmd_bar.set_text)

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
                        'Delete': (lambda: self.object_manager.delete_object(), 'Delete'),
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
                'Layers': (self.layer_window.exec, 'Ctrl+L'),
                'Render': (self.start_render, None)
            },
            theme_manager=self.tm)
        self.setMenuBar(self.menu_bar)

        self.update_recent_files_menu()

        horizontal_layout.addWidget(self.draw_bar)
        middle_column.addWidget(self.plot)

        horizontal_layout.addLayout(middle_column)
        horizontal_layout.addLayout(right_column)

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
        self.setStyleSheet(self.tm.bg_style_sheet)
        # self.cmd_bar.set_styles()
        self.draw_bar.set_styles()
        # self.inspector_bar.set_styles()
        self.plot.set_styles()
        self.properties_bar.set_styles()
        # self.tool_bar.set_styles()
        self.layer_window.set_styles()
        self.menu_bar.set_styles()
        self.top_bar.set_styles()

    def closeEvent(self, a0) -> None:
        self.settings_manager.serialize()
        super(MainWindow, self).closeEvent(a0)


