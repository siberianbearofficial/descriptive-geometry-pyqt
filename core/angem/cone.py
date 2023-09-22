import core.angem as ag
from core.angem.vector import Vector


class Cone(ag.Object3D):
    def __init__(self, point, point2_or_height, radius1, radius2=0, vector=Vector(0, 0, 1)):
        self.center1 = point
        self.radius1 = radius1
        self.radius2 = radius2
        if isinstance(point2_or_height, ag.Point):
            self.center2 = point2_or_height
            self.vector = Vector(self.center1, self.center2)
            self.height = abs(self.vector)
        else:
            self.height = point2_or_height
            self.vector = vector
            self.center2 = self.center1 + vector * self.height / abs(vector)

        circle = ag.Circle(self.center1, self.radius1, self.vector)
        polygons = [circle]
        if self.radius2:
            polygons.append(ag.Circle(self.center2, self.radius2, self.vector))
        else:
            for p1, p2 in circle.get_pairs():
                polygons.append(ag.Polygon2D.from_points(p1, p2, self.center2))
        super().__init__(polygons)
