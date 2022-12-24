class RealPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tuple(self):
        return self.x, self.y

    def __add__(self, other):
        return RealPoint(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return RealPoint(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return RealPoint(self.x * other, self.y * other)

    @staticmethod
    def from_point(point, axis, plane='xz'):
        if plane == 'xy':
            return RealPoint(axis.p2.x - point.x, point.y + axis.p1.y)
        return RealPoint(axis.p2.x - point.x, axis.p1.y - point.z)
