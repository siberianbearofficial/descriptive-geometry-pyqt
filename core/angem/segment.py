import core.angem as ag


class Segment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.line = ag.Line(p1, p2)

    def __str__(self):
        return 'Segment({0}, {1})'.format(self.p1, self.p2)

    def intersection(self, other):
        if isinstance(other, ag.Segment):
            point = self.line.intersection(other.line)
            if not _point_between(point, other.p1, other.p2):
                return None
        else:
            point = self.line.intersection(other, 1)
        # if point:
        #     print(point, self.p1, self.p2, _point_between(point, self.p1, self.p2))
        if point is None or not _point_between(point, self.p1, self.p2):
            return None
        return point

    def projection_xy(self):
        if self.p1.x == self.p2.x and self.p1.y == self.p2.y:
            return ag.Point(self.p1.x, self.p1.y, 0)
        return Segment(self.p1.projection_xy(), self.p2.projection_xy())

    def projection_xz(self):
        if self.p1.x == self.p2.x and self.p1.z == self.p2.z:
            return ag.Point(self.p1.x, 0, self.p1.y)
        return Segment(self.p1.projection_xz(), self.p2.projection_xz())


EPS = 1e-8


def _point_between(point, p1, p2):
    if (point.x - EPS > p1.x and point.x - EPS > p2.x) or (point.x + EPS < p1.x and point.x + EPS < p2.x):
        return False
    if (point.y > p1.y - EPS and point.y - EPS > p2.y) or (point.y + EPS < p1.y and point.y + EPS < p2.y):
        return False
    if (point.z > p1.z - EPS and point.z - EPS > p2.z) or (point.z + EPS < p1.z and point.z + EPS < p2.z):
        return False
    return True
