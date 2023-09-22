import core.angem as ag


class Object3D:
    def __init__(self, polygons: list[ag.Polygon2D]):
        self.polygons = polygons

    def intersection(self, other):
        if isinstance(other, ag.Plane):
            lst = []
            for el1 in self.polygons:
                obj = el1.intersection(other)
                if obj:
                    lst.append(obj)
            return ag.IntersectionLine(lst)
        if isinstance(other, ag.Object3D):
            lst = []
            for el1 in self.polygons:
                for el2 in other.polygons:
                    obj = el1.intersection(el2)
                    if obj:
                        lst.append(obj)
            print(len(lst))
            return ag.IntersectionLine(lst)
