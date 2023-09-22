
class Spline3D:
    def __init__(self, *points):
        if isinstance(points[0], list):
            points = points[0]
        p1, p2, p3 = points[0], points[1], points[2]
        pl = Plane(p1, p2, p3)
        l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & pl.normal)
        l2 = Line(p2 + Vector(p2, p3) * 0.5, Vector(p2, p3) & pl.normal)
        c = l1.intersection(l2, 1e20)
        pl3 = Plane(p2, Vector(c, p2), pl.normal)
        v = pl.normal & Vector(c, p2)
        self.array = [(points[0],), (points[1], Arc(p1, p2, c))]
        self.points = points
        for i in range(2, len(points)):
            p1, p2 = points[i - 1], points[i]
            if distance(p1, p2) == 0:
                continue
            pl1 = Plane(Vector(p1, p2), p1 + Vector(p1, p2) * 0.5)
            pl2 = Plane(p1, p2, v)
            c = pl1.intersection(pl2).intersection(pl3)
            pl3 = Plane(p2, Vector(c, p2), Plane(p1, p2, c).normal)
            v = pl.normal & Vector(c, p2)

            self.array.append((p2, Arc(p1, p2, c)))

    def intersection(self, other):
        lst = []
        for i in range(1, len(self.array)):
            res = self.array[i][1].intersection(other)
            if res is None:
                continue
            if isinstance(res, tuple):
                lst.extend(list(res))
            else:
                lst.append(res)
        return tuple(lst)

    @staticmethod
    def convert_points_to_splines(points, max_dist):
        for i in range(len(points)):
            if points[i] != tuple():
                lst = [[el] for el in points[i]]
                break
        else:
            return
        for i in range(i + 1, len(points)):
            for point in points[i]:
                for group in lst:
                    if distance(point, group[-1]) <= max_dist:
                        group.append(point)
                        break
                else:
                    lst.append([point])
        res = [lst[0]]
        max_dist *= 2
        for i in range(1, len(lst)):
            for j in range(len(res)):
                d1 = distance(lst[i][0], res[j][0])
                d2 = distance(lst[i][-1], res[j][0])
                d3 = distance(lst[i][0], res[j][-1])
                d4 = distance(lst[i][-1], res[j][-1])
                if d1 <= max_dist and d4 <= max_dist:
                    res[j] += list(reversed(lst[i])) + [res[j][0]]
                elif d2 <= max_dist and d3 <= max_dist:
                    res[j] += lst[i] + [res[j][0]]
                elif d1 <= max_dist:
                    res[j] = list(reversed(lst[i])) + res[j]
                elif d2 <= max_dist:
                    res[j] += lst[i]
                elif d3 <= max_dist:
                    res[j] = lst[i] + res[j]
                elif d4 <= max_dist:
                    res[j] += list(reversed(lst[i]))
                else:
                    res.append(lst[i])
        res2 = []
        for el in res:
            if len(el) >= 3:
                try:
                    res2.append(Spline3D(el))
                except Exception:
                    pass
        return tuple(res2)

