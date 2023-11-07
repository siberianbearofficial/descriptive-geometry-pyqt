import math

from core.angem import Object3D, Polygon2D
from core.angem.utils import distance
from core.angem.circle import Circle
from core.angem.line import Line
from core.angem.plane import Plane
from core.angem.point import Point
from core.angem.vector import Vector
from core.config import GRAPHICS


class Sphere(Object3D):
    COUNT = 2 * GRAPHICS

    def __init__(self, center, radius):
        if not isinstance(center, Point):
            raise ValueError('Center is not a point')
        self.center = center
        self.radius = radius
        
        polygons = []
        for m in [1, -1]:
            last_circle = Circle(self.center, self.radius)
            vector = last_circle.normal * m
            for i in range(1, Sphere.COUNT + 1):
                h = self.radius * i * 0.9999 / Sphere.COUNT
                r = math.sqrt(self.radius ** 2 - h ** 2)
                circle = Circle(self.center + vector.set_len(h), r, vector)
                for lst1, lst2 in zip(last_circle.get_pairs(), circle.get_pairs()):
                    polygons.append(Polygon2D.from_points(lst1[0], lst2[0], lst2[1], lst1[1]))
                last_circle = circle
        super().__init__(polygons)

    def __str__(self):
        return f'Sphere: {self.center}, R = {self.radius}'

