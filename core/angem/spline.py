
class Spline:
    def __init__(self, plane, *points):
        self.plane = plane
        if isinstance(points[0], list):
            points = points[0]
        p1, p2, p3 = points[0], points[1], points[2]
        l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & self.plane.normal)
        l2 = Line(p2 + Vector(p2, p3) * 0.5, Vector(p2, p3) & self.plane.normal)
        c = l1.intersection(l2, 1e20)
        self.array = [(points[0],), (points[1], Arc(p1, p2, c)), (points[2], Arc(p2, p3, c))]
        self.points = points
        for i in range(2, len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            if distance(p1, p2) == 0:
                continue
            l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & self.plane.normal)
            l2 = Line(c, p1)
            c = l1.intersection(l2, 1e20)

            try:
                self.array.append((p2, Arc(p1, p2, c)))
            except Exception:
                pass

    def intersection(self, other):
        if isinstance(other, Plane):
            return self.intersection(self.plane.intersection(other))
        lst = []
        for i in range(1, len(self.array)):
            res = self.array[i][1].intersection(other, False)
            if res is None:
                continue
            if isinstance(res, tuple):
                lst.extend(list(res))
            else:
                lst.append(res)
        return tuple(lst)

