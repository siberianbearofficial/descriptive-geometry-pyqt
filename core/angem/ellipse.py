

class Ellipse:
    def __init__(self, obj1, obj2, obj3):
        self.center = obj1
        self.point_a1 = obj2 if abs(Vector(obj1, obj2)) > abs(Vector(obj1, obj3)) else obj3
        self.point_a2 = self.center + -Vector(self.center, self.point_a1)
        self.point_b1 = obj3 if abs(Vector(obj1, obj2)) > abs(Vector(obj1, obj3)) else obj2
        self.point_b2 = self.center + -Vector(self.center, self.point_b1)
        self.a = abs(Vector(self.center, self.point_a1))
        self.b = abs(Vector(self.center, self.point_b1))
        self.c = (self.a ** 2 - self.b**2) ** 0.5
        self.f1 = self.center + Vector(self.center, self.point_a1) * (self.c / abs(Vector(self.center, self.point_a1)))
        self.f2 = self.center + Vector(self.center, self.point_a1) * -(self.c / abs(Vector(self.center, self.point_a1)))
        self.plane = Plane(self.center, self.point_a1, self.point_b1)

