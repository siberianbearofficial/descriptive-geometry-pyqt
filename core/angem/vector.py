import core.angem as ag


class Vector:
    def __init__(self, x, y, z=0.0):
        if isinstance(x, ag.Point) and isinstance(y, ag.Point):
            self.x = y.x - x.x
            self.y = y.y - x.y
            self.z = y.z - x.z
        else:
            self.x = x
            self.y = y
            self.z = z

    @staticmethod
    def from_str(s, function=int):
        s = s.replace('{', '')
        s = s.replace('}', '')
        s = s.replace(',', ' ')
        s = s.split()
        return Vector(function(s[0]), function(s[1]), function(s[2]))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: int | float):
        return Vector(self.x / other, self.y / other, self.z / other)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        raise ValueError(f'unsupported operand type(s) for +: "Vector" and "{other.__class__.__name__}"')

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        raise ValueError(f'unsupported operand type(s) for -: "Vector" and "{other.__class__.__name__}"')

    def __and__(self, other):
        if isinstance(other, Vector):
            return Vector(self.y * other.z - self.z * other.y,
                          self.z * other.x - self.x * other.z,
                          self.x * other.y - self.y * other.x)
        raise ValueError(f'unsupported operand type(s) for &: "Vector" and "{other.__class__.__name__}"')

    def __str__(self):
        return f"vector({self.x}, {self.y}, {self.z})"

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __or__(self, other):
        if isinstance(other, Vector):
            return abs((self.x * other.y) - (self.y * other.x)) < 1e-10 and \
                   abs((self.x * other.z) - (self.z * other.x)) < 1e-10 and \
                   abs((self.y * other.z) - (self.z * other.y)) < 1e-10
        raise ValueError(f'unsupported operand type(s) for |: "Vector" and "{other.__class__.__name__}"')

    def is_null_vector(self):
        return not (self.x or self.y or self.z)

    def __bool__(self):
        return not (self.x or self.y or self.z)

    def perpendicular(self):
        if self.y or self.z:
            return self & Vector(1, 0, 0)
        return self & Vector(0, 1, 1)

    def set_len(self, new_len: float | int):
        return self / abs(self) * new_len
