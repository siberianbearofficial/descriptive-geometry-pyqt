from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont

import utils.maths.angem as ag


class CmdBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.command = None
        self.plot = None

        self.setGeometry(160, 640, 711, 61)
        self.setStyleSheet("background-color: #B2B2B2;\n"
                           "border-radius: 10px;")

        font = QFont()
        font.setFamily("Alegreya Sans SC Medium")
        font.setPointSize(6)

        strange_widget = QWidget(self)
        strange_widget.setFixedSize(self.geometry().size())

        # Layout
        self.layout = QVBoxLayout(strange_widget)
        self.layout.setContentsMargins(15, 10, 0, 10)
        self.layout.setSpacing(0)

        # Past
        self.past = QLabel()
        self.past.setFont(font)
        self.past.setStyleSheet("color: rgba(60, 64, 72, 0.5);")
        self.layout.addWidget(self.past)

        # Present
        self.present = QLabel()
        self.present.setFont(font)
        self.present.setStyleSheet("color: rgba(60, 64, 72, 0.5);")
        self.layout.addWidget(self.present)

        # Future
        self.future = QLineEdit()
        font.setPointSize(8)
        self.future.setFont(font)
        self.future.setStyleSheet("color: rgb(60, 64, 72);")

        self.future.returnPressed.connect(self.on_enter_pressed)

        self.layout.addWidget(self.future)

        self.commands = {'segment': ag.Segment, 'point': ag.Point, 'line': ag.Line, 'plane': ag.Plane,
                         'vector': ag.Vector, 'ellipse': ag.Ellipse, 'sphere': ag.Sphere,
                         'cylinder': ag.Cylinder, 'cone': ag.Cone, 'spline': ag.Spline, 'spline3d': ag.Spline3D,
                         'circle': ag.Circle, 'distance': ag.distance, 'angle': ag.angle, 'clear': self.command_clear,
                         'draw': self.command_draw_object, 'help': CmdBar.command_help, 'mtrx': ag.Matrix,
                         'save': self.command_serialize, 'load': self.command_deserialize,
                         'reset': self.command_reset}

        self.variables = self.commands.copy()

    def set_text(self, text):
        self.past.setText(self.present.text())
        self.present.setText(str(text))

    def on_enter_pressed(self):
        self.set_text(self.future.text())
        self.process_command(self.future.text())
        self.future.setText('')

    def set_command(self, command):
        self.command = command
        return self

    def set_plot(self, plot):
        # TODO: REMOVE THIS STRANGE THING :)
        self.plot = plot
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
        # TODO: refactor this to make it more readable
        print(
            '''
            Commands:
            segment(point, point) - creates segment
            point(x, y, z) - creates point
            line(point, point) - creates line
            print(*args) - prints args
            clear() - clears screen
            draw(*args) - draws args
            help() - prints this message

            Some tips:
            Typing command without parentheses won't execute it.
            You can't use variables to store results of commands.
            Typical usage looks like this:
            segment(point(0, 0, 0), point(1, 1, 1))   # this creates segment but doesn't draw or print it')
            draw(segment(point(0, 0, 0), point(1, 1, 1)))
            segment(point(0, 0, 0), point(1, 1, 1)))
            '''
        )

    def command_clear(self, index=-1):
        self.plot.clear(index)

    def command_serialize(self):
        pass

    def command_deserialize(self):
        pass

    def command_draw_object(self, *args):
        for obj in args:
            self.plot.add_object(obj)
