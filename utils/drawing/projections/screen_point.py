import math

from utils.color import *


class ScreenPoint:
    def __init__(self, x, y, color=None, thickness=4):
        self.x = x
        self.y = y
        self.color = color
        self.thickness = thickness

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return f"point({self.x:.1f}, {self.y:.1f})"

    def move(self, x, y):
        self.x += x
        self.y += y

    def distance(self, other: 'ScreenPoint'):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class ThinScreenPoint:
    def __init__(self, x, y, color=None, thickness=2):
        self.x = x
        self.y = y
        self.color = color
        self.thickness = thickness

    def __iter__(self):
        yield self.x
        yield self.y

    def move(self, x, y):
        self.x += x
        self.y += y

