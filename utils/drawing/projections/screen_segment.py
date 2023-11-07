import math

from PyQt6.QtCore import Qt

from utils.drawing.projections.projection_manager import ScreenPoint
from utils.color import *


class ScreenSegment:
    def __init__(self, p1, p2, color=None, thickness=3, line_type=Qt.PenStyle.SolidLine):
        if isinstance(p1, tuple):
            p1 = ScreenPoint(*p1)
        if isinstance(p2, tuple):
            p2 = ScreenPoint(*p2)
        self.p1 = p1
        self.p2 = p2
        self._vector = _2DVector(p2.x - p1.x, p2.y - p1.y)
        self._d = -self._vector.x * self.p1.x - self._vector.y * self.p1.y
        self.color = color
        self.thickness = thickness
        self.line_type = line_type

    def x(self, y):
        return self._vector.x * (y - self.p1.y) / self._vector.y + self.p1.x

    def y(self, x):
        return self._vector.y * (x - self.p1.x) / self._vector.x + self.p1.y

    def distance(self, point: tuple[int] | ScreenPoint, as_line=False):
        if isinstance(point, tuple):
            point = ScreenPoint(*point)
        return self.nearest(point, as_line).distance(point)

    def intersection_as_line(self, other: 'ScreenSegment'):
        if not self._vector.x:
            return ScreenPoint(self.p1.x, other.y(self.p1.x))
        if not self._vector.y:
            return ScreenPoint(other.x(self.p1.y), self.p1.y)
        if not other._vector.x:
            return ScreenPoint(other.p1.x, self.y(other.p1.x))
        if not other._vector.y:
            return ScreenPoint(self.x(other.p1.y), other.p1.y)

        y = (self._vector.x / self._vector.y * self.p1.y - other._vector.x / other._vector.y * other.p1.y -
             self.p1.x + other.p1.x) / (self._vector.x / self._vector.y - other._vector.x / other._vector.y)
        return ScreenPoint(self.x(y=y), y)

    def intersection(self, other):
        point = self.intersection_as_line(other)
        if min(self.p1.x, self.p2.x) <= point.x <= max(self.p1.x, self.p2.x) and \
                min(self.p1.y, self.p2.y) <= point.y <= max(self.p1.y, self.p2.y) and \
                min(other.p1.x, other.p2.x) <= point.x <= max(other.p1.x, other.p2.x) and \
                min(other.p1.y, other.p2.y) <= point.y <= max(other.p1.y, other.p2.y):
            return point
        return None

    def nearest(self, point: ScreenPoint, as_line=False):
        perp = ScreenSegment(point, ScreenPoint(point.x + self._vector.y, point.y - self._vector.x))
        intersection = self.intersection_as_line(perp)
        if as_line or intersection is None:
            return intersection
        if min(self.p1.x, self.p2.x) <= intersection.x <= max(self.p1.x, self.p2.x) and \
                min(self.p1.y, self.p2.y) <= intersection.y <= max(self.p1.y, self.p2.y):
            return intersection
        if intersection.distance(self.p1) < intersection.distance(self.p2):
            return self.p1
        return self.p2

    # def y(self, x):
    #     return self.k * x + self.b
    #
    # def x(self, y):
    #     if self.k is None:
    #         return self.p1.x
    #     return (y - self.b) / self.k


class _2DVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return _2DVector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return _2DVector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return _2DVector(self.x * other.x, self.y * other.y)

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __bool__(self):
        return self.x and self.y
