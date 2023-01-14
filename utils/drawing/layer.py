from utils.drawing.general_object import GeneralObject
import pygame as pg

from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment


class Layer:
    def __init__(self, plot, hidden=False):
        self.plot = plot
        self.hidden = hidden
        self.objects = []

    def add_object(self, ag_object, color):
        self.objects.append(GeneralObject(self.plot, ag_object, color))

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        self.objects = []
