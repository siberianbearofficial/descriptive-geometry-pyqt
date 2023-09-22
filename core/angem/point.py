import core.angem as ag


class Point:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_str(s, function=int):
        if '(' not in s or ')' not in s or not (1 <= s.count(',') <= 2):
            raise ValueError
        s = s.replace('(', '')
        s = s.replace(')', '')
        if s.count(',') == 1:
            s += ',0'
        s = s.replace(',', ' ')
        s = s.split()
        return Point(function(s[0]), function(s[1]), function(s[2]))

    def __add__(self, other):
        if isinstance(other, ag.Vector):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        raise ValueError(f'unsupported operand type(s) for +: "Point" and "{other.__class__.__name__}"')

    def __str__(self):
        return f"point({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"

    def is_on(self, other):
        if isinstance(other, ag.Line):
            return ag.Vector(self, other.point) | other.vector
        if isinstance(other, ag.Plane):
            return abs(other.normal.x * self.x + other.normal.y * self.y + other.normal.z * self.z + other.d) < 1e-10
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def projection_xy(self):
        return Point(self.x, self.y, 0)

    def projection_xz(self):
        return Point(self.x, 0, self.z)
