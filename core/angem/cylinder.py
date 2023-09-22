import core.angem as ag
from core.angem.point import Point
from core.angem.vector import Vector


class Cylinder(ag.Object3D):
    def __init__(self, point, point2_or_height, radius, vector=Vector(0, 0, 1)):
        self.center1 = point
        self.radius = radius
        if isinstance(point2_or_height, Point):
            self.center2 = point2_or_height
            self.vector = Vector(self.center1, self.center2)
            self.height = abs(self.vector)
        else:
            self.height = point2_or_height
            self.vector = vector
            self.center2 = self.center1 + vector * (self.height / abs(vector))

        circle = ag.Circle(self.center1, self.radius, self.vector)
        polygons = [circle, ag.Circle(self.center2, self.radius, self.vector)]
        for p1, p2 in circle.get_pairs():
            polygons.append(ag.Polygon2D.from_points(p1, p1 + self.vector, p2 + self.vector, p2))
        super().__init__(polygons)

