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

        self.plot = Plot(self, (0, 65), (self.brp[0], self.brp[1] - 40))
        self.command_line = CommandLine(self)
        # self.toolbar = Toolbar(self)

        self.toolbars = []

        self.toolbars.append(Toolbar2(self, (0, 0), (1000, 25)))
        self.toolbars[0].add_button('file', lambda: self.select_toolbar(1), (10, 0), (42, 20))
        self.toolbars[0].add_button('drawing', lambda: self.select_toolbar(2), (57, 0), (76, 20))
        self.toolbars[0].add_button('view', lambda: self.select_toolbar(3), (138, 0), (33, 20))

        self.toolbars.append(Toolbar2(self, (0, 25), (1000, 65), hidden=True))

        self.toolbars.append(Toolbar2(self, (0, 25), (1000, 65)))
        self.toolbars[2].add_button('point', lambda: self.plot.create_point(), (10, 0))
        self.toolbars[2].add_button('segment', lambda: self.plot.create_segment(), (45, 0))
        self.toolbars[2].add_button('line', lambda: self.plot.create_line(), (80, 0))
        self.toolbars[2].add_button('plane', lambda: self.plot.create_plane(), (115, 0))
        self.toolbars[2].add_button('circle', lambda: print('circle'), (150, 0))

        self.toolbars.append(Toolbar2(self, (0, 25), (1000, 65), hidden=True))
        self.toolbars[3].add_button('minus', lambda: self.plot.zoom_out(), (10, 0))
        self.toolbars[3].add_button('plus', lambda: self.plot.zoom_in(), (45, 0))

        self.full_update_toolbars()

    def update(self):
        pg.display.update()

    def clicked(self):
        self.click_pos = pg.mouse.get_pos()
        for toolbar in self.toolbars:
            if toolbar.clicked_on(self.click_pos):
                return
        if self.command_line.clicked_on(self.click_pos):
            return
        # TODO: if clicked on plot
        self.plot.clicked(self.click_pos)

    def full_update_toolbars(self):
        pg.draw.rect(self.screen, (255, 255, 255), (0, self.brp[1] - 40, self.brp[0], self.brp[1]))
        for toolbar in self.toolbars:
            toolbar.draw()

    def select_toolbar(self, index):
        for i in range(1, 4):
            self.toolbars[i].hidden = True
        self.toolbars[index].hidden = False
        self.full_update_toolbars()
        self.plot.full_update()
