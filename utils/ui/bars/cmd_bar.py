from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit

import core.angem as ag
from utils.ui.widgets.widget import Widget
from utils.color import *


class CmdBar(Widget):
    def __init__(self, parent, font_manager, theme_manager):
        super().__init__(parent)

        self.command = None
        self.command_to_plot = False
        self.theme_manager = theme_manager

        self.setGeometry(160, 640, 711, 61)    # TODO: REMOVE THIS!!!

        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(15, 10, 0, 10)
        self.layout.setSpacing(0)

        # Past
        self.past = QLabel()
        self.past.setFont(font_manager.medium())
        self.past.setStyleSheet("color: rgba(60, 64, 72, 0.5);")
        self.layout.addWidget(self.past)

        # Present
        self.present = QLabel()
        self.present.setFont(font_manager.medium())
        self.present.setStyleSheet("color: rgba(60, 64, 72, 0.5);")
        self.layout.addWidget(self.present)

        # Future
        self.future = QLineEdit()
        self.future.setFont(font_manager.bold(size=12))
        self.future.setStyleSheet("color: rgb(60, 64, 72);")

        self.future.returnPressed.connect(self.on_enter_pressed)

        self.layout.addWidget(self.future)

        self.commands = {'segment': ag.Segment, 'point': ag.Point, 'line': ag.Line, 'plane': ag.Plane,
                         # 'vector': ag.Vector, 'ellipse': ag.Ellipse, 'sphere': ag.Sphere,
                         # 'cylinder': ag.Cylinder, 'cone': ag.Cone, 'spline': ag.Spline, 'spline3d': ag.Spline3D,
                         # 'circle': ag.Circle, 'distance': ag.distance, 'angle': ag.angle, 'clear': self.command_clear,
                         # 'draw': self.command_draw_object, 'help': CmdBar.command_help, 'mtrx': ag.Matrix,
                         # 'save': self.command_serialize, 'load': self.command_deserialize,
                         'reset': self.command_reset}

        self.variables = self.commands.copy()

    def set_text(self, text):
        self.past.setText(self.present.text())
        self.present.setText(str(text))

    def set_command_to_plot(self, flag):
        self.command_to_plot = flag

    def on_enter_pressed(self):
        self.set_text(self.future.text())
        if self.command_to_plot:
            # self.plot.cmd_command(self.future.text())  # TODO: fix points with cmd
            pass
        else:
            self.process_command(self.future.text())
        self.future.setText('')

    def set_command(self, command):
        self.command = command
        return self

    def execute_command(self, cmd):
        try:
            return eval(cmd, self.variables)
        except Exception as ex:
            self.set_text('Error: {}'.format(ex))

    def process_command(self, command):
        if '=' in command:
            i = command.index('=')
            var, arg = command[:i].strip(), command[i + 1:].strip()
            for symbol in '-+*/ ().,':
                if symbol in var:
                    arg = command.strip()
                    res = self.execute_command(arg)
                    if res:
                        self.set_text(res)
                    break
            if var != 'reset':
                self.variables[var] = self.execute_command(arg)
            else:
                raise ValueError("You can't change command reset")
        else:
            arg = command.strip()
            res = self.execute_command(arg)
            if res:
                self.set_text(res)

    def command_reset(self, function=None):
        if function:
            if function in self.variables:
                self.variables[function] = self.commands[function]
            else:
                self.variables.pop(function)
        else:
            self.variables = self.commands.copy()

    @staticmethod
    def command_help():
        print('Unfortunately we can\'t help you right now, try again later')

    def command_clear(self, index=-1):
        self.clear_plot(index)

    def command_serialize(self):
        pass

    def command_deserialize(self):
        pass

    def command_draw_object(self, *args):
        for obj in args:
            self.add_object(obj)

    def clear_plot(self, index=-1):
        pass

    def add_object(self, obj):
        pass

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.get_style_sheet(self.__class__.__name__))
