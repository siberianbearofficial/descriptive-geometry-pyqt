
class Tor:
    def __init__(self, center, radius, tube_radius, vector=Vector(0, 0, 1)):
        self.center = center
        self.radius = radius
        self.tube_radius = tube_radius
        self.vector = vector

    def intersection(self, other):
        if isinstance(other, Plane):
            if other.normal | self.vector:
                p = Line(self.center, self.vector).intersection(other)
                if d := distance(p, self.center) > self.tube_radius:
                    return
                return Circle(p, self.radius + (self.tube_radius ** 2 - d ** 2) ** 0.5, self.vector), \
                       Circle(p, self.radius - (self.tube_radius ** 2 - d ** 2) ** 0.5, self.vector)
            if self.center.is_on(other):
                c1, c2 = Circle(self.center, self.radius, self.vector).intersection(other)
                return Circle(c1, self.tube_radius, other.normal), Circle(c2, self.tube_radius, other.normal)
        if isinstance(other, Cylinder) or isinstance(other, Cone):
            if self.vector | other.vector:
                c1 = self.center + self.vector * (self.tube_radius / abs(self.vector))
                c2 = self.center + -self.vector * (self.tube_radius / abs(self.vector))
                p1, p2 = c1, c2
                if self.vector * other.vector > 0:
                    if distance(c1, other.center2) < distance(p1, p2):
                        p1, p2 = c1, other.center2
                    if distance(other.center1, c2) < distance(p1, p2):
                        p1, p2 = other.center1, c2
                    if distance(other.center1, other.center2) < distance(p1, p2):
                        p1, p2 = other.center1, other.center2
                else:
                    if distance(c1, other.center1) < distance(p1, p2):
                        p1, p2 = c1, other.center1
                    if distance(other.center2, c2) < distance(p1, p2):
                        p1, p2 = other.center2, c2
                    if distance(other.center2, other.center1) < distance(p1, p2):
                        p1, p2 = other.center2, other.center1
                v = Vector(p1, p2) * 0.01
                lst1, lst2, lst3, lst4 = [], [], [], []
                for i in range(101):
                    c1, c2 = self.intersection(Plane(v, p1 + v * i))
                    p = c1.intersection(other.intersection(Plane(v, p1 + v * i)))
                    if isinstance(p, tuple):
                        lst1.append(p[0])
                        lst2.append(p[1])
                    elif p is not None:
                        lst1.append(p)
                    p = c2.intersection(other.intersection(Plane(v, p1 + v * i)))
                    if isinstance(p, tuple):
                        lst3.append(p[0])
                        lst4.append(p[1])
                    elif p is not None:
                        lst2.append(p)
                return Spline3D(*lst1, *reversed(lst2)), Spline3D(*lst3, *reversed(lst4))

