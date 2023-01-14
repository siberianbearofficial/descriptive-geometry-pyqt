from utils.drawing.command_line import CommandLine
from utils.drawing.plot import Plot
from utils.drawing.toolbar import Toolbar, Toolbar2

import pygame as pg


class Screen:

    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.tlp = (0, 0)
        self.brp = (width, height)
        self.click_pos = None

        self.screen = pg.display.set_mode((width, height))
        self.title = title
        pg.display.set_caption(title)

        self.screen.fill((255, 255, 255))

        self.plot = Plot(self, (0, 40), (self.brp[0], self.brp[1] - 40))
        self.command_line = CommandLine(self)
        # self.toolbar = Toolbar(self)

        self.toolbar = Toolbar2(self)
        self.toolbar.add_button('point', lambda: self.plot.create_point(), (10, 5))
        self.toolbar.add_button('segment', lambda: self.plot.create_segment(), (45, 5))
        self.toolbar.add_button('line', lambda: print('line'), (80, 5))
        self.toolbar.add_button('plane', lambda: print('plane'), (115, 5))
        self.toolbar.add_button('circle', lambda: print('circle'), (150, 5))

    def update(self):
        pg.display.update()

    def clicked(self):
        self.click_pos = pg.mouse.get_pos()
        if self.toolbar.clicked_on(self.click_pos):
            return
        if self.command_line.clicked_on(self.click_pos):
            return
        # TODO: if clicked on plot
        self.plot.clicked(self.click_pos)
