from pygame_widgets.button import ButtonArray
import pygame as pg


class Toolbar:

    def __init__(self, screen):
        self.screen = screen
        self.active_tool = 0
        self.buttons = ButtonArray(
            # Mandatory Parameters
            screen.screen, 10, 35, 500, 20,
            (4, 1),
            border=1,  # Distance between buttons and edge of array
            # texts=('Point', 'Segment', '-', '-'),  # Sets the texts of each
            # button (counts left to right then top to bottom)

            images=(pg.image.load('test.bmp'), pg.image.load('test.bmp'), pg.image.load('test.bmp'), pg.image.load('test.bmp')),

            # When clicked, print number
            onClicks=(
                lambda: self.change_activation(1), lambda: self.change_activation(2), lambda: self.change_activation(3),
                lambda: self.change_activation(4))
        )

        self.change_activation(0)

    def change_activation(self, tool):
        if self.active_tool == tool:
            self.active_tool = 0
        else:
            self.active_tool = tool

        for i in range(len(self.buttons.buttons)):
            if i == self.active_tool - 1:
                self.buttons.buttons[i].inactiveColour = (100, 200, 100)
            else:
                self.buttons.buttons[i].inactiveColour = (200, 200, 200)

        if self.active_tool == 0:
            self.screen.plot.stop_listening()
        elif self.active_tool == 1:
            self.screen.plot.point_selection()
        elif self.active_tool == 2:
            self.screen.plot.segment_selection()
        elif self.active_tool == 3:
            self.screen.plot.segment_selection()
        elif self.active_tool == 4:
            self.screen.plot.segment_selection()

    def clicked_on(self, pos):
        left = self.buttons.getX()
        top = self.buttons.getY()
        right = left + self.buttons.getWidth()
        bottom = top + self.buttons.getHeight()
        return left <= pos[0] <= right and top <= pos[1] <= bottom
