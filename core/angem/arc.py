import math

from core.angem.line import Line
from core.angem.plane import Plane
from core.angem.vector import Vector


class Arc:
    def __init__(self, p1, p2, center, big_arc=False):
        # if abs((r := distance(p1, center)) - distance(p2, center)) > 1e-10:
        #     raise ValueError
        self.center = center
        self.radius = distance(p1, center)
        self.plane = Plane(p1, p2, center)
        self.p1 = p1
        self.p2 = p2
        self.normal = self.plane.normal
        self.big_arc = big_arc
        self.vector_cos = Vector(center, p1)
        self.vector_sin = -(self.vector_cos & self.normal) * (self.radius / abs(self.vector_cos & self.normal))
        self.angle = self.get_angle(p2)

    def get_angle(self, point):
        vector = Vector(self.center, point)
        a = angle(self.vector_cos, vector)
        if self.big_arc and vector * self.vector_sin > 0:
            return a - 2 * math.pi
        if not self.big_arc and vector * self.vector_sin <= 0:
            return a - 2 * math.pi
        return a

    def intersection(self, other, check_plane=True):
        if isinstance(other, Line):
            if not check_plane or other.is_on(self.plane):
                if abs((d := distance(self.center, other)) - self.radius) < 1e-12:
                    return Line(self.center, self.normal & other.vector).intersection(other)
                if d > self.radius:
                    return None
                s = math.sqrt(self.radius ** 2 - d ** 2)
                v1 = other.vector * (s / abs(other.vector))
                v2 = self.normal & other.vector * (d / abs(self.normal & other.vector))
                if v2 * Vector(self.center, other.point) < 0:
                    v2 *= -1
                p1, p2 = self.center + v1 + v2, self.center + -v1 + v2
                lst = []
                if abs(self.get_angle(p1)) < abs(self.angle):
                    lst.append(p1)
                if abs(self.get_angle(p2)) < abs(self.angle):
                    lst.append(p2)
                return tuple(lst)
        if isinstance(other, Plane):
            return self.intersection(self.plane.intersection(other))
        circle = Circle(self.center, self.radius, self.normal)
        try:
            p = circle.intersection(other, False)
        except Exception:
            p = other.intersection(circle)
        if p is None:
            return
        if isinstance(p, tuple):
            p1, p2 = p
            lst = []
            if abs(self.get_angle(p1)) < abs(self.angle):
                lst.append(p1)
            if abs(self.get_angle(p2)) < abs(self.angle):
                lst.append(p2)
            return tuple(lst)
        if abs(self.get_angle(p)) < abs(self.angle):
            return p,
