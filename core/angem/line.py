import core.angem as ag


class Line:
    def __init__(self, obj1, obj2):
        if isinstance(obj1, ag.Point) and isinstance(obj2, ag.Vector):
            self.point = obj1
            if isinstance(obj2, ag.Point):
                self.vector = ag.Vector(obj1, obj2)
            else:
                self.vector = obj2
        elif isinstance(obj1, ag.Point) and isinstance(obj2, ag.Point):
            self.point = obj1
            self.vector = ag.Vector(obj1, obj2)
        else:
            raise ValueError(
                f'unsupported operand type(s) for Line: "{obj1.__class__.__name__}" and "{obj2.__class__.__name__}"')

    def __str__(self):
        return f'(x - {self.point.x}) / {self.vector.x} = (y - {self.point.y}) /' \
               f'{self.vector.y} = (z - {self.point.z}) / {self.vector.z}'

    def __or__(self, other):
        if isinstance(other, Line):
            return self.vector | other.vector
        if isinstance(other, ag.Vector):
            return self.vector | other
        if hasattr(other, '__or__'):
            return other | self
        raise ValueError(f'unsupported operand type(s) for |: "Line" and "{other.__class__.__name__}"')

    def intersection(self, other, eps=1e-6):
        if isinstance(other, ag.Plane):
            if self | other:
                return None
            k = -(other.normal.x * self.point.x + other.normal.y * self.point.y + other.normal.z * self.point.z +
                  other.d) / \
                (other.normal.x * self.vector.x + other.normal.y * self.vector.y + other.normal.z * self.vector.z)
            x = self.point.x + self.vector.x * k
            y = self.point.y + self.vector.y * k
            z = self.point.z + self.vector.z * k
            return ag.Point(x, y, z)
        if isinstance(other, Line):
            if abs((self.vector & other.vector) * ag.Vector(self.point, other.point)) > eps or self | other:
                return None
            if self.vector.x == 0 and other.vector.x == 0:
                if self.vector.y != 0 and other.vector.y != 0:
                    y = (self.vector.z / self.vector.y * self.point.y - other.vector.z / other.vector.y * other.point.y
                         - self.point.z + other.point.z) / (
                                self.vector.z / self.vector.y - other.vector.z / other.vector.y)
                    return ag.Point(self.point.x, y, self.z(y=y))
                else:
                    z = (self.vector.y / self.vector.z * self.point.z - other.vector.y / other.vector.z * other.point.z
                         - self.point.y + other.point.y) / (
                                    self.vector.y / self.vector.z - other.vector.y / other.vector.z)
                    return ag.Point(self.point.x, self.y(z=z), z)
            if self.vector.y == 0 and other.vector.y == 0:
                if self.vector.x != 0 and other.vector.x != 0:
                    x = (self.vector.z / self.vector.x * self.point.x - other.vector.z / other.vector.x * other.point.x
                         - self.point.z + other.point.z) / (
                                self.vector.z / self.vector.x - other.vector.z / other.vector.x)
                    return ag.Point(x, self.point.y, self.z(x=x))
                else:
                    z = (self.vector.x / self.vector.z * self.point.z - other.vector.x / other.vector.z * other.point.z
                         - self.point.x + other.point.x) / (
                                    self.vector.x / self.vector.z - other.vector.x / other.vector.z)
                    return ag.Point(self.x(z=z), self.point.y, z)
            if self.vector.z == 0 and other.vector.z == 0:
                if self.vector.x != 0 and other.vector.x != 0:
                    x = (self.vector.y / self.vector.x * self.point.x - other.vector.y / other.vector.x * other.point.x
                         - self.point.y + other.point.y) / (
                                self.vector.y / self.vector.x - other.vector.y / other.vector.x)
                    return ag.Point(x, self.y(x=x), self.point.z)
                else:
                    y = (self.vector.x / self.vector.y * self.point.y - other.vector.x / other.vector.y * other.point.y
                         - self.point.x + other.point.x) / (
                                self.vector.x / self.vector.y - other.vector.x / other.vector.y)
                    return ag.Point(self.x(y=y), y, self.point.z)
            if self.vector.x == 0:
                return ag.Point(self.point.x, other.y(x=self.point.x), other.z(x=self.point.x))
            if self.vector.y == 0:
                return ag.Point(other.x(y=self.point.y), self.point.y, other.z(y=self.point.y))
            if self.vector.z == 0:
                return ag.Point(other.x(z=self.point.z), other.y(z=self.point.z), self.point.z)
            if other.vector.x == 0:
                return ag.Point(other.point.x, self.y(x=other.point.x), self.z(x=other.point.x))
            if other.vector.y == 0:
                return ag.Point(self.x(y=other.point.y), other.point.y, self.z(y=other.point.y))
            if other.vector.z == 0:
                return ag.Point(self.x(z=other.point.z), self.y(z=other.point.z), other.point.z)
            y = (self.vector.x / self.vector.y * self.point.y - other.vector.x / other.vector.y * other.point.y -
                 self.point.x + other.point.x) / (self.vector.x / self.vector.y - other.vector.x / other.vector.y)
            return ag.Point(self.x(y=y), y, self.z(y=y))
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def is_on(self, other):
        if isinstance(other, ag.Plane):
            return self.point.is_on(other) and abs(self.vector * other.normal) < 1e-12
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def x(self, y=None, z=None):
        if y is not None:
            return self.vector.x * (y - self.point.y) / self.vector.y + self.point.x
        if z is not None:
            return self.vector.x * (z - self.point.z) / self.vector.z + self.point.x
        raise ValueError('no operand')

    def y(self, x=None, z=None):
        if x is not None:
            return self.vector.y * (x - self.point.x) / self.vector.x + self.point.y
        if z is not None:
            return self.vector.y * (z - self.point.z) / self.vector.z + self.point.y
        raise ValueError('no operand')

    def z(self, x=None, y=None):
        if x is not None:
            return self.vector.z * (x - self.point.x) / self.vector.x + self.point.z
        if y is not None:
            return self.vector.z * (y - self.point.y) / self.vector.y + self.point.z
        raise ValueError('no operand')

    def projection_xy(self):
        if self.vector.x == 0 and self.vector.y == 0:
            return ag.Point(self.point.x, self.point.y, 0)
        return Line(ag.Point(self.point.x, self.point.y, 0), ag.Vector(self.vector.x, self.vector.y, 0))

    def projection_xz(self):
        if self.vector.x == 0 and self.vector.z == 0:
            return ag.Point(self.point.x, 0, self.point.z)
        return Line(ag.Point(self.point.x, 0, self.point.z), ag.Vector(self.vector.x, 0, self.vector.z))

    def cut_by_x(self, min_x, max_x):
        return ag.Segment(ag.Point(min_x, self.y(x=min_x), self.z(x=min_x)), ag.Point(max_x, self.y(x=max_x), self.z(x=max_x)))

    def cut_by_y(self, min_y, max_y):
        return ag.Segment(ag.Point(self.x(y=min_y), min_y, self.z(y=min_y)), ag.Point(self.x(y=max_y), max_y, self.z(y=max_y)))

    def cut_by_z(self, min_z, max_z):
        return ag.Segment(ag.Point(self.x(z=min_z), self.y(z=min_z), min_z), ag.Point(self.x(z=max_z), self.y(z=max_z), max_z))
