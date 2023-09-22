import math

import core.angem as ag
from core.angem import Polygon2D
from core.angem.vector import Vector


class Circle(Polygon2D):
    COUNT = 20

    def __init__(self, center, radius, normal=Vector(0, 0, 1)):
        self.center = center
        if radius < 0:
            raise ValueError
        self.radius = radius
        self.normal = normal
        self.plane = ag.Plane(self.normal, self.center)

        points = []
        if self.radius:
            vector_sin = self.normal.perpendicular().set_len(self.radius)
            vector_cos = (vector_sin & self.normal).set_len(self.radius)
            for i in range(Circle.COUNT):
                points.append(self.center + vector_sin * math.sin(2 * math.pi * (i + 1) / Circle.COUNT) +
                              vector_cos * math.cos(2 * math.pi * (i + 1) / Circle.COUNT))
        super().__init__(self.plane, points)

    def __str__(self):
        if self.normal | Vector(0, 0, 1):
            return f'Circle: {self.center}, R = {self.radius}'
        return f'Circle: {self.center}, R = {self.radius}, normal {self.normal}'

    def intersection(self, other, check_plane=True):
        # if isinstance(other, ag.Line):
        #     if other.is_on(ag.Plane(self.normal, self.center)):
        #         if abs((d := ag.distance(self.center, other)) - self.radius) < 1e-12:
        #             print('= radius')
        #             return ag.Line(self.center, self.normal & other.vector).intersection(other)
        #         if d > self.radius:
        #             return None
        #         s = math.sqrt(self.radius ** 2 - d ** 2)
        #         v1 = other.vector * (s / abs(other.vector))
        #         v2 = self.normal & other.vector * (d / abs(self.normal & other.vector))
        #         if v2 * Vector(self.center, other.point) < 0:
        #             v2 *= -1
        #         return self.center + v1 + v2, self.center + -v1 + v2
        # if isinstance(other, ag.Plane):
        #     return self.intersection(self.plane.intersection(other))
        # if isinstance(other, Circle):
        #     if not check_plane or (self.normal | other.normal and other.center.is_on(self.plane)):
        #         dist = ag.distance(self.center, other.center)
        #         if self.radius + other.radius < dist or \
        #                 min(self.radius, other.radius) + dist < max(self.radius, other.radius):
        #             return
        #         x = (self.radius ** 2 - other.radius ** 2 + dist ** 2) / 2 / dist
        #         if x > self.radius:
        #             return None
        #         r = (self.radius ** 2 - x ** 2) ** 0.5
        #         p = self.center + Vector(self.center, other.center) * (x / dist)
        #         v = Vector(self.center, other.center) & self.normal * \
        #             (r / abs(Vector(self.center, other.center) & self.normal))
        #         return p + v, p + -v
        pass

    def area(self):
        return math.pi * self.radius ** 2
