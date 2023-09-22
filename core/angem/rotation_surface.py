class RotationSurface:
    def __init__(self, point1, point2, spline):
        self.center1 = point1
        self.center2 = point2
        self.vector = Vector(point1, point2)
        self.spline1 = spline
        vector = (spline.plane.normal & self.vector) * (1 / abs(spline.plane.normal & self.vector))
        if vector * Vector(point1, spline.array[0][0]) < 0:
            vector *= -1
        self.spline2 = Spline(
            spline.plane, *[spline.array[i][0] + (vector * (-2 * distance(spline.array[i][0], Line(point1, point2))))
                            for i in range(len(spline.array))])
        self.radius1 = distance(point1, spline.intersection(Line(point1, self.vector & spline.plane.normal))[0])
        self.radius2 = distance(point2, spline.intersection(Line(point2, self.vector & spline.plane.normal))[0])

    def intersection(self, other):
        if isinstance(other, Plane) and other.normal | self.vector:
            p = Line(self.center1, self.center2).intersection(other)
            return Circle(p, distance(p, self.spline1.intersection(Line(
                p, self.vector & self.spline1.plane.normal))[0]), self.vector)
        if isinstance(other, Plane):
            return intersection_rotation_surface_and_plane(self, other)
        if isinstance(other, Cylinder) or isinstance(other, Cone) or isinstance(other, RotationSurface):
            if self.vector | other.vector:
                p1, p2 = self.center1, self.center2
                if self.vector * other.vector > 0:
                    if distance(self.center1, other.center2) < distance(p1, p2):
                        p1, p2 = self.center1, other.center2
                    if distance(other.center1, self.center2) < distance(p1, p2):
                        p1, p2 = other.center1, self.center2
                    if distance(other.center1, other.center2) < distance(p1, p2):
                        p1, p2 = other.center1, other.center2
                else:
                    if distance(self.center1, other.center1) < distance(p1, p2):
                        p1, p2 = self.center1, other.center1
                    if distance(other.center2, self.center2) < distance(p1, p2):
                        p1, p2 = other.center2, self.center2
                    if distance(other.center2, other.center1) < distance(p1, p2):
                        p1, p2 = other.center2, other.center1
                v = Vector(p1, p2) * 0.01
                lst1, lst2 = [], []
                for i in range(101):
                    p = self.intersection(Plane(v, p1 + v * i)).intersection(other.intersection(Plane(v, p1 + v * i)))
                    if isinstance(p, tuple):
                        lst1.append(p[0])
                        lst2.append(p[1])
                    elif p is not None:
                        lst1.append(p)
                return Spline3D(*lst1), Spline3D(*lst2)
        return intersection_rotation_surface_and_rotation_surface(self, other)
