import random
import pygame as pg
from pygame_widgets.textbox import TextBox
import utils.maths.angem as ag
from utils.drawing.general_object import GeneralObject


class CommandLine:

    def __init__(self, screen):
        self.screen = screen

        self.textbox = TextBox(self.screen.screen, 10, screen.brp[1] - 30, screen.width - 20, 20, inactiveColour=(255, 255, 255),
                               activeColour=(200, 200, 200), textColour=(0, 0, 0), borderColour=(64, 64, 64), radius=0,
                               borderThickness=1, font=pg.font.SysFont('Courier', 12))
        self.textbox.onSubmit = self.output

        self.commands = {'segment': ag.Segment, 'point': ag.Point, 'line': ag.Line, 'plane': ag.Plane,
                         'vector': ag.Vector,
                         'circle': ag.Circle, 'distance': ag.distance, 'angle': ag.angle, 'clear': self.command_clear,
                         'draw': self.command_draw_object, 'help': CommandLine.command_help}  # , 'pp': place_point}

    def output(self):
        self.process_command(self.textbox.getText())
        self.textbox.setText('')

    def execute_command(self, cmd):
        try:
            return eval(cmd, self.commands)
        except Exception as ex:
            print('Error:', ex)

    def process_command(self, command):
        if '=' in command:
            i = command.index('=')
            var, arg = command[:i].strip(), command[i + 1:].strip()
            for symbol in '-+*/ ().,':
                if symbol in var:
                    arg = command.strip()
                    res = self.execute_command(arg)
                    if res:
                        print(res)
                    break
            self.commands[var] = self.execute_command(arg)
        else:
            arg = command.strip()
            res = self.execute_command(arg)
            if res:
                print(res)

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
            
            Рисование точек мышкой работает так:
            1. Кликнуть на кнопку Point (должна активироваться, т.е. стать зеленой)
            2. Кликнуть на нужное место на экране для выбора координаты X
            3. Аналогично для Y
            4. Аналогично для Z
            После этого появится черная точка с выбранными координатами.
            Чтобы отключить режим, нужно нажать еще раз на кнопку Point или любую другую из Toolbar
            (в этом случае будет отключен этот режим и сразу включен другой)
            '''
        )

    def command_clear(self, index=-1):
        self.screen.plot.clear(index)

    def command_draw_object(self, *args):
        for obj in args:
            random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
            # self.screen.plot.draw_object(obj, random_color)
            self.screen.plot.layers[0].add_object(obj, random_color)
            self.screen.plot.layers[0].objects[-1].draw()

    def clicked_on(self, pos):
        left = self.textbox.getX()
        top = self.textbox.getY()
        right = left + self.textbox.getWidth()
        bottom = top + self.textbox.getHeight()
        return left <= pos[0] <= right and top <= pos[1] <= bottom
