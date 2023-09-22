import math

from core.angem import Object3D, Polygon2D
from core.angem.utils import distance
from core.angem.circle import Circle
from core.angem.line import Line
from core.angem.plane import Plane
from core.angem.point import Point
from core.angem.vector import Vector


class Sphere(Object3D):
    COUNT = 10

    def __init__(self, center, radius):
        if not isinstance(center, Point):
            raise ValueError('Center is not a point')
        self.center = center
        self.radius = radius
        
        polygons = []
        last_circle = Circle(self.center, self.radius)
        vector = last_circle.normal
        for i in range(1, Sphere.COUNT):
            h = self.radius * i / Sphere.COUNT
            r = math.sqrt(self.radius ** 2 - h ** 2)
            circle = Circle(self.center + vector.set_len(h), r, vector)
            for lst1, lst2 in zip(last_circle.get_pairs(), circle.get_pairs()):
                polygons.append(Polygon2D.from_points(lst1[0], lst2[0], lst2[1], lst1[1]))
            last_circle = circle
        last_circle = Circle(self.center, self.radius)
        vector = last_circle.normal * -1
        for i in range(1, Sphere.COUNT):
            h = self.radius * i / Sphere.COUNT
            r = math.sqrt(self.radius ** 2 - h ** 2)
            circle = Circle(self.center + vector.set_len(h), r, vector)
            for lst1, lst2 in zip(last_circle.get_pairs(), circle.get_pairs()):
                polygons.append(Polygon2D.from_points(lst1[0], lst2[0], lst2[1], lst1[1]))
            last_circle = circle
        super().__init__(polygons)

    def __str__(self):
        return f'Sphere: {self.center}, R = {self.radius}'

