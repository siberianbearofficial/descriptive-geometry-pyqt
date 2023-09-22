import core.angem as ag


class Plane:
    def __init__(self, object1, object2=None, object3=None):
        if isinstance(object1, ag.Line) and isinstance(object2, ag.Line):
            self.point = object1.point
            self.vector1 = object1.vector
            self.vector2 = object2.vector
            self.normal = self.vector1 & self.vector2
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, ag.Line) and isinstance(object2, ag.Point):
            self.point = object1.point
            self.vector1 = object1.vector
            self.vector2 = ag.Vector(self.point, object2)
            self.normal = self.vector1 & self.vector2
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, ag.Point) and isinstance(object2, ag.Line):
            self.point = object2.point
            self.vector1 = object2.vector
            self.vector2 = ag.Vector(self.point, object1)
            self.normal = self.vector2 & self.vector1
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, ag.Vector) and object2 is not None:
            self.normal = object1
            if isinstance(object2, ag.Point):
                self.point = object2
                self.d = -object1.x * object2.x - object1.y * object2.y - object1.z * object2.z
            else:
                self.d = object2
                if self.normal * ag.Vector(0, 0, 1) != 0:
                    self.point = ag.Point(0, 0, -self.d / self.normal.z)
                elif self.normal * ag.Vector(0, 1, 0) != 0:
                    self.point = ag.Point(0, -self.d / self.normal.y, 0)
                elif self.normal * ag.Vector(1, 0, 0) != 0:
                    self.point = ag.Point(-self.d / self.normal.x, 0, 0)
            self.vector1, self.vector2 = self.generate_vectors()
            return
        if isinstance(object1, str):
            p = Plane.from_str(object1)
            self.normal = p.normal
            self.d = p.d
            if self.normal * ag.Vector(0, 0, 1) != 0:
                self.point = ag.Point(0, 0, -self.d / self.normal.z)
            elif self.normal * ag.Vector(0, 1, 0) != 0:
                self.point = ag.Point(0, -self.d / self.normal.y, 0)
            elif self.normal * ag.Vector(1, 0, 0) != 0:
                self.point = ag.Point(-self.d / self.normal.x, 0, 0)
            self.vector1, self.vector2 = self.generate_vectors()
            return
        self.point = object1
        if isinstance(object2, ag.Point):
            self.vector1 = ag.Vector(object1, object2)
        else:
            self.vector1 = object2
        if isinstance(object3, ag.Point):
            self.vector2 = ag.Vector(object1, object3)
        else:
            self.vector2 = object3
        self.normal = self.vector1 & self.vector2
        self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z

    def __str__(self):
        return f'{self.normal.x:.1f}x + {self.normal.y:.1f}y + {self.normal.z:.1f}z + {self.d:.1f} = 0'

    def __or__(self, other):
        if isinstance(other, Plane):
            return self.normal | other.normal
        if isinstance(other, ag.Line):
            return abs(ag.angle(self, other)) < 1e-10
        raise ValueError(f'unsupported operand type(s) for |:  "Plane" and "{other.__class__.__name__}"')

    def intersection(self, other):
        if isinstance(other, Plane):
            if self | other:
                return None

            try:
                y = (-other.d + other.normal.x * self.d / self.normal.x) / (other.normal.y - other.normal.x *
                                                                            self.normal.y / self.normal.x)
                x = -(self.normal.y * y + self.d) / self.normal.x
                return ag.Line(ag.Point(x, y, 0), self.normal & other.normal)
            except Exception:
                try:
                    z = (-other.d + other.normal.y * self.d / self.normal.y) / (other.normal.z - other.normal.y *
                                                                                self.normal.z / self.normal.y)
                    y = -(self.normal.z * z + self.d) / self.normal.y
                    return ag.Line(ag.Point(0, y, z), self.normal & other.normal)
                except Exception:
                    x = (-other.d + other.normal.z * self.d / self.normal.z) / (other.normal.x - other.normal.z *
                                                                                self.normal.x / self.normal.z)
                    z = -(self.normal.x * x + self.d) / self.normal.z
                    return ag.Line(ag.Point(x, 0, z), self.normal & other.normal)
        if isinstance(other, ag.Line):
            k = -(self.normal.x * other.point.x + self.normal.y * other.point.y + self.normal.z * other.point.z +
                  self.d) / \
                (self.normal.x * other.vector.x + self.normal.y * other.vector.y + self.normal.z * other.vector.z)
            x = other.point.x + other.vector.x * k
            y = other.point.y + other.vector.y * k
            z = other.point.z + other.vector.z * k
            return ag.Point(x, y, z)
        raise TypeError(f'unsupported operand type: "{other.__class__.__name__}"')

    @staticmethod
    def from_str(s, function=int):
        lst = s.split()
        for i in range(len(lst) - 1):
            lst[i] = lst[i].strip()
            if lst[i] == '-':
                lst[i] = ''
                lst[i + 1] = '-' + lst[i + 1].strip()
            elif lst[i] == '+':
                lst[i] = ''
        while '' in lst:
            lst.remove('')
        if lst[-2] != '=' or lst[-1] != '0':
            raise ValueError('invalid equation')
        a, b, c, d = 0, 0, 0, 0
        for i in range(len(lst) - 2):
            if 'x' in lst[i]:
                lst[i] = lst[i].replace('x', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                a = function(lst[i])
            elif 'y' in lst[i]:
                lst[i] = lst[i].replace('y', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                b = function(lst[i])
            elif 'z' in lst[i]:
                lst[i] = lst[i].replace('z', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                c = function(lst[i])
            elif lst[i] != '+' and lst[i] != '-':
                d = function(lst[i])
            if a == 0 and b == 0 and c == 0:
                raise ValueError('invalid equation')
        return Plane(ag.Vector(a, b, c), d)

    def x(self, y, z):
        return (-self.normal.y * y - self.normal.z * z - self.d) / self.normal.x

    def y(self, x, z):
        return (-self.normal.x * x - self.normal.z * z - self.d) / self.normal.y

    def z(self, x, y):
        return (-self.normal.x * x - self.normal.y * y - self.d) / self.normal.z

    def trace_xy(self):
        return self.intersection(Plane(ag.Vector(0, 0, 1), ag.Point(0, 0, 0)))

    def trace_xz(self):
        return self.intersection(Plane(ag.Vector(0, 1, 0), ag.Point(0, 0, 0)))

    def trace_yz(self):
        return self.intersection(Plane(ag.Vector(1, 0, 0), ag.Point(0, 0, 0)))

    def projection_xy(self):
        return self.trace_xy()

    def projection_xz(self):
        return self.trace_xz()

    def horizontal(self, point):
        return ag.Line(point, self.normal & ag.Vector(0, 0, 1))

    def frontal(self, point):
        return ag.Line(point, self.normal & ag.Vector(0, 1, 0))

    def generate_vectors(self):
        if self.normal.x != 0:
            x = -(self.normal.y + self.normal.z) / self.normal.x
            v = ag.Vector(x, 1, 1)
            return v, self.normal & v
        elif self.normal.y != 0:
            y = -(self.normal.x + self.normal.z) / self.normal.y
            v = ag.Vector(1, y, 1)
            return v, self.normal & v
        else:
            z = -(self.normal.x + self.normal.y) / self.normal.z
            v = ag.Vector(1, 1, z)
            return v, self.normal & v
