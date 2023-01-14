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

        self.toolbars.append(Toolbar2(self, (10, 5), (500, 25)))
        self.toolbars[0].add_button('file', lambda: self.select_toolbar(1), (0, 0), size=(39, 20))
        self.toolbars[0].add_button('drawing', lambda: self.select_toolbar(2), (44, 0), size=(76, 20))
        self.toolbars[0].add_button('layer', lambda: self.select_toolbar(3), (125, 0), size=(39, 20))
        self.toolbars[0].add_button('view', lambda: self.select_toolbar(4), (169, 0), size=(33, 20))

        self.toolbars.append(Toolbar2(self, (10, 30), (500, 65), hidden=True))
        self.toolbars[1].add_button('newfile', lambda: print('new'), (0, 0))
        self.toolbars[1].add_button('openfile', lambda: print('open'), (35, 0))
        self.toolbars[1].add_button('save', lambda: print('save'), (70, 0))
        self.toolbars[1].add_button('saveas', lambda: print('save as'), (105, 0))

        self.toolbars.append(Toolbar2(self, (10, 30), (500, 65)))
        self.toolbars[2].add_button('point', lambda: self.plot.create_point(), (0, 0))
        self.toolbars[2].add_button('segment', lambda: self.plot.create_segment(), (35, 0))
        self.toolbars[2].add_button('line', lambda: self.plot.create_line(), (70, 0))
        self.toolbars[2].add_button('plane', lambda: print('plane'), (105, 0))
        self.toolbars[2].add_button('circle', lambda: print('circle'), (140, 0))
        self.toolbars[2].add_button('sphere', lambda: print('sphere'), (175, 0))

        self.toolbars.append(Toolbar2(self, (10, 30), (500, 65), hidden=True))

        self.toolbars.append(Toolbar2(self, (10, 30), (500, 65), hidden=True))
        self.toolbars[4].add_button('minus', lambda: self.plot.zoom_out(), (0, 0))
        self.toolbars[4].add_button('plus', lambda: self.plot.zoom_in(), (35, 0))

        for tb in self.toolbars:
            tb.draw()

    def update(self):
        pg.display.update()

    def clicked(self):
        self.click_pos = pg.mouse.get_pos()
        for tb in self.toolbars:
            if tb.clicked_on(self.click_pos):
                return
        if self.command_line.clicked_on(self.click_pos):
            return
        # TODO: if clicked on plot
        self.plot.clicked(self.click_pos)

    def select_toolbar(self, index):
        for i in range(1, 5):
            if i == index:
                self.toolbars[i].hidden = False
            else:
                self.toolbars[i].hidden = True
        for tb in self.toolbars:
            tb.draw()

    def full_update_toolbars(self):
        pg.draw.rect(self.screen, (255, 255, 255), (0, 0, self.brp[0], 65))
        pg.draw.rect(self.screen, (255, 255, 255), (0, self.brp[1] - 40, self.brp[0], self.brp[1]))
        for tb in self.toolbars:
            tb.draw()
