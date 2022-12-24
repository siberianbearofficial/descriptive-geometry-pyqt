class RealPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tuple(self):
        return self.x, self.y

    @staticmethod
    def from_point(point, axis, plane='xz'):
        if plane == 'xy':
            return RealPoint(axis.p2.x - point.x, point.y + axis.p1.y)
        return RealPoint(axis.p2.x - point.x, axis.p1.y - point.z)
