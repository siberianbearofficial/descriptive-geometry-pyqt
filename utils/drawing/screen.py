from utils.drawing.command_line import CommandLine
from utils.drawing.plot import Plot
from utils.drawing.menu import Menu

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

        self.plot = Plot(self, (0, 60), (self.brp[0], self.brp[1] - 40))
        self.command_line = CommandLine(self)
        self.menu = Menu(self)

        self.menu.full_update_toolbars()

    def update(self):
        pg.display.update()

    def clicked(self):
        self.click_pos = pg.mouse.get_pos()
        if self.menu.clicked_on(self.click_pos):
            return
        if self.command_line.clicked_on(self.click_pos):
            return
        # TODO: if clicked on plot
        self.plot.clicked(self.click_pos)
