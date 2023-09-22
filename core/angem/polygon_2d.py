import core.angem as ag


class Polygon2D:
    def __init__(self, plane: ag.Plane, points: list[ag.Point] | tuple[ag.Point]):
        self.plane = plane
        self.points = points

    def __iter__(self):
        for el in self.points:
            yield el

    @staticmethod
    def from_points(*args: ag.Point):
        plane = ag.Plane(args[0], args[1], args[2])
        return Polygon2D(plane, args)

    def line_intersection(self, other: ag.Line):
        intersections = []
        for p1, p2 in self.get_pairs():
            segment = ag.Segment(p1, p2)
            point = segment.intersection(other)
            if point:
                intersections.append(point)
        if len(intersections) > 2:
            # print(len(self.points), *self.points)
            # print(len(intersections), *intersections)
            # raise ValueError("Вроде как, здесь не должно быть больше двух пересечений")
            print(f"Тут должно быть не больше 2 пересечений, но найдено {len(intersections)}")
            intersections = intersections[:2]
        return intersections

    def intersection(self, other):
        if isinstance(other, ag.Plane):
            line = self.plane.intersection(other)
            if line is None:
                return None
            lst = self.line_intersection(line)
            if len(lst) != 2:
                return None
            return ag.Segment(*lst)

        line = self.plane.intersection(other.plane)
        if line is None:
            return None
        lst1 = self.line_intersection(line)
        lst2 = other.line_intersection(line)
        if len(lst1) != 2 or len(lst2) != 2:
            return None
        for var in ['x', 'y', 'z']:
            if getattr(line.vector, var):
                return _cut(*lst1, *lst2, var)

    def get_pairs(self):
        for i in range(len(self.points)):
            yield self.points[i - 1], self.points[i]


def _cut(p1, p2, p3, p4, var='x'):
    if getattr(p2, var) < getattr(p1, var):
        p1, p2 = p2, p1
    if getattr(p4, var) < getattr(p3, var):
        p3, p4 = p4, p3
    point1 = p1 if getattr(p1, var) > getattr(p3, var) else p3
    point2 = p2 if getattr(p2, var) < getattr(p4, var) else p4
    if getattr(point1, var) > getattr(point2, var):
        return None
    return ag.Segment(point1, point2)
