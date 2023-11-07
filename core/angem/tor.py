import math

import core.angem as ag
from core.angem import Circle, Polygon2D
from core.config import GRAPHICS


class Tor(ag.Object3D):
    COUNT = GRAPHICS * 2

    def __init__(self, center, radius, tube_radius, vector=ag.Vector(0, 0, 1)):
        self.center = center
        self.radius = radius
        self.tube_radius = tube_radius
        self.vector = vector

        polygons = []
        for m in [1, -1]:
            vector = self.vector * m
            last_outer = Circle(self.center, self.radius + self.tube_radius, vector)
            try:
                last_inner = Circle(self.center, self.radius - self.tube_radius, vector)
            except ValueError:
                last_inner = None
            for i in range(1, Tor.COUNT + 1):
                h = self.tube_radius * i * 0.9999 / Tor.COUNT
                r = self.radius + math.sqrt(self.tube_radius ** 2 - h ** 2)
                circle = Circle(self.center + vector.set_len(h), r, vector)
                for lst1, lst2 in zip(last_outer.get_pairs(), circle.get_pairs()):
                    polygons.append(Polygon2D.from_points(lst1[0], lst2[0], lst2[1], lst1[1]))
                last_outer = circle
                r = self.radius - math.sqrt(self.tube_radius ** 2 - h ** 2)
                if r > 0:
                    circle = Circle(self.center + vector.set_len(h), r, vector)
                    if last_inner is not None:
                        for lst1, lst2 in zip(last_inner.get_pairs(), circle.get_pairs()):
                            polygons.append(Polygon2D.from_points(lst1[0], lst2[0], lst2[1], lst1[1]))
                    last_inner = circle

        super().__init__(polygons)
