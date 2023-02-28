import utils.maths.angem as ag
from utils.drawing.screen_point import ScreenPoint, ScreenPoint2
from utils.drawing.screen_segment import ScreenSegment
from utils.drawing.screen_circle import ScreenCircle
import math


class ProjectionManager:

    def __init__(self, plot):
        self.plot = plot
        self.axis = plot.axis
        self.zoom = 1
        self.camera_pos = (0, 0)

    def get_projection(self, obj, plane, color):
        if isinstance(obj, ag.Point):
            return self.point_projections(obj, plane, color)

        elif isinstance(obj, ag.Circle):
            return self.circle_projections(obj, plane, color)

        elif isinstance(obj, ag.Arc):
            return self.arc_projections(obj, plane, color)

        elif isinstance(obj, ag.Segment):
            point1 = self.point_projections(obj.p1, plane, color)
            point2 = self.point_projections(obj.p2, plane, color)
            return self.segment_projections(obj, plane, color), point1, point2

        elif isinstance(obj, ag.Plane):
            return self.plane_projections(obj, plane, color)

        elif isinstance(obj, ag.Line):
            return self.line_projections(obj, plane, color)

        elif isinstance(obj, ag.Ellipse):
            return self.ellipse_projections(obj, plane, color)

        elif isinstance(obj, ag.Sphere):
            return self.sphere_projections(obj, plane, color)

        elif isinstance(obj, ag.Cylinder):
            return self.cylinder_projections(obj, plane, color)

        elif isinstance(obj, ag.Cone):
            return self.cone_projections(obj, plane, color)

        elif isinstance(obj, ag.RotationSurface):
            return self.rotation_surface_projections(obj, plane, color)

        elif isinstance(obj, ag.Tor):
            return self.tor_projections(obj, plane, color)

        elif isinstance(obj, ag.Spline) or isinstance(obj, ag.Spline3D):
            return self.spline_projections(obj, plane, color)

    def point_projections(self, obj, plane, color):
        return ScreenPoint(self.plot, *self.convert_ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                           color)

    def segment_projections(self, obj, plane, color):
        p1 = ScreenPoint(self.plot,
                         *self.convert_ag_coordinate_to_screen_coordinate(obj.p1.x, obj.p1.y, obj.p1.z, plane),
                         color)
        p2 = ScreenPoint(self.plot,
                         *self.convert_ag_coordinate_to_screen_coordinate(obj.p2.x, obj.p2.y, obj.p2.z, plane),
                         color)

        return ScreenSegment(self.plot, p1, p2, color)

    def line_projections(self, obj, plane, color):
        if plane == 'xy':
            if obj.vector.x == 0 and obj.vector.y == 0:
                return self.point_projections(obj.point, plane, color)
            elif obj.vector.y == 0:
                return self.segment_projections(
                    obj.cut_by_x(self.convert_screen_x_to_ag_x(self.plot.brp[0] + 1),
                                 self.convert_screen_x_to_ag_x(self.plot.tlp[0] - 1)),
                    plane, color)
            else:
                return self.segment_projections(
                    obj.cut_by_y(self.convert_screen_y_to_ag_y(self.axis.lp[1] - 1),
                                 self.convert_screen_y_to_ag_y(self.plot.brp[1] + 1)),
                    plane, color)
        else:
            if obj.vector.x == 0 and obj.vector.z == 0:
                return self.point_projections(obj.point, plane, color)
            elif obj.vector.z == 0:
                return self.segment_projections(
                    obj.cut_by_x(self.convert_screen_x_to_ag_x(self.plot.brp[0] + 1),
                                 self.convert_screen_x_to_ag_x(self.plot.tlp[0] - 1)),
                    plane, color)
            else:
                return self.segment_projections(
                    obj.cut_by_z(self.convert_screen_y_to_ag_z(self.axis.lp[1] - 1),
                                 self.convert_screen_y_to_ag_z(self.plot.tlp[1] + 1)),
                    plane, color)

    def plane_projections(self, obj, plane, color):
        if plane == 'xy':
            return self.get_projection(obj.trace_xy(), plane, color)
        return self.get_projection(obj.trace_xz(), plane, color)

    def circle_projections(self, obj, plane, color):
        if obj.radius == 0:
            return self.get_projection(obj.center, plane, color)
        if obj.normal.x == 0 and (obj.normal.y if plane == 'xy' else obj.normal.z) == 0:
            return ScreenCircle(self.plot, self.get_projection(obj.center, plane, color), obj.radius * self.zoom,
                                color),
        if obj.normal * (ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)) == 0:
            point1, point2 = obj.intersection(
                ag.Line(obj.center, obj.normal & (ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0))))
            return self.segment_projections(ag.Segment(point1, point2), plane, color),
        vector_sin = obj.normal & (obj.normal + ag.Vector(2, 1, 1))
        vector_sin = vector_sin * (obj.radius / abs(vector_sin))
        vector_cos = obj.normal & vector_sin
        vector_cos = vector_cos * (obj.radius / abs(vector_cos))
        step = 1 / self.zoom / obj.radius
        x, lst = 0, []
        while x < 1.57:
            s, c = math.sin(x), math.cos(x)
            lst.append(self.get_point(obj.center + vector_sin * s + vector_cos * c, plane, color))
            lst.append(self.get_point(obj.center + -vector_sin * s + vector_cos * c, plane, color))
            lst.append(self.get_point(obj.center + vector_sin * s + -vector_cos * c, plane, color))
            lst.append(self.get_point(obj.center + -vector_sin * s + -vector_cos * c, plane, color))
            x += step
        return tuple(lst)

    def ellipse_projections(self, obj, plane, color):
        # TODO: Исправить эллипсы
        lst = []
        step = 1 / self.zoom
        c1, c2 = obj.a + obj.c, obj.a - obj.c
        while c1 > obj.a - obj.c - step / 2:
            res = ag.Sphere(obj.f1, c1).intersection(ag.Sphere(obj.f2, c2))
            if res is not None:
                res = res.intersection(obj.plane)
                if res is not None:
                    if isinstance(res, tuple):
                        for el in res:
                            lst.append(self.get_point(el, plane, color))
                    else:
                        lst.append(self.get_point(res, plane, color))
            c2 += step
            c1 -= step
        return lst

    def sphere_projections(self, obj, plane, color):
        return ScreenCircle(self.plot, self.get_projection(obj.center, plane, color), obj.radius * self.zoom, color)

    def cylinder_projections(self, obj, plane, color):
        v = ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)
        if obj.vector | v:
            return self.circle_projections(ag.Circle(obj.center1, obj.radius, obj.vector), plane, color)
        res = self.circle_projections(ag.Circle(obj.center1, obj.radius, obj.vector), plane, color), \
              self.circle_projections(ag.Circle(obj.center2, obj.radius, obj.vector), plane, color), \
              self.segment_projections(ag.Segment(obj.center1 + (obj.vector & v * (obj.radius / abs(obj.vector & v))),
                                                  obj.center2 + (obj.vector & v * (obj.radius / abs(obj.vector & v)))),
                                       plane, color), \
              self.segment_projections(ag.Segment(obj.center1 + -(obj.vector & v * (obj.radius / abs(obj.vector & v))),
                                                  obj.center2 + -(obj.vector & v * (obj.radius / abs(obj.vector & v)))),
                                       plane, color)
        return unpack_inner_tuples(res)

    def cone_projections(self, obj, plane, color):
        v = ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)
        if obj.vector | v:
            res = self.circle_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), plane, color), \
                  self.circle_projections(ag.Circle(obj.center1, obj.radius2, obj.vector), plane, color)
        else:
            res = self.circle_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), plane, color), \
                  self.circle_projections(ag.Circle(obj.center2, obj.radius2, obj.vector), plane, color), \
                  self.segment_projections(
                      ag.Segment(obj.center1 + (obj.vector & v * (obj.radius1 / abs(obj.vector & v))),
                                 obj.center2 + (obj.vector & v * (obj.radius2 / abs(obj.vector & v)))),
                      plane, color), \
                  self.segment_projections(
                      ag.Segment(obj.center1 + -(obj.vector & v * (obj.radius1 / abs(obj.vector & v))),
                                 obj.center2 + -(obj.vector & v * (obj.radius2 / abs(obj.vector & v)))),
                      plane, color)
        return unpack_inner_tuples(res)

    def arc_projections(self, obj, plane, color):
        step = 1 / self.zoom / obj.radius
        x, lst = 0, []
        if obj.angle >= 0:
            while x < obj.angle:
                s, c = math.sin(x), math.cos(x)
                lst.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, plane, color))
                x += step
        else:
            while x > obj.angle:
                s, c = math.sin(x), math.cos(x)
                lst.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, plane, color))
                x -= step
        return tuple(lst)

    def tor_projections(self, obj, plane, color):
        if obj.tube_radius > obj.radius:
            circles = *self.get_projection(ag.Circle(obj.center, obj.radius + obj.tube_radius, obj.vector), plane,
                                           color), \
                      *self.get_projection(ag.Circle(obj.center + obj.vector * (obj.tube_radius / abs(obj.vector)),
                                                     obj.radius, obj.vector), plane, color), \
                      *self.get_projection(ag.Circle(obj.center + obj.vector * (-obj.tube_radius / abs(obj.vector)),
                                                     obj.radius, obj.vector), plane, color)
        else:
            circles = *self.get_projection(ag.Circle(obj.center, obj.radius + obj.tube_radius, obj.vector), plane,
                                           color), \
                      *self.get_projection(ag.Circle(obj.center, obj.radius - obj.tube_radius, obj.vector), plane,
                                           color), \
                      *self.get_projection(ag.Circle(obj.center + obj.vector * (obj.tube_radius / abs(obj.vector)),
                                                     obj.radius, obj.vector), plane, color), \
                      *self.get_projection(ag.Circle(obj.center + obj.vector * (-obj.tube_radius / abs(obj.vector)),
                                                     obj.radius, obj.vector), plane, color)
        if (obj.vector * ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)) == 0:
            c1, c2 = obj.intersection(ag.Plane(ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1),
                                               obj.center))
            return *circles, *self.get_projection(c1, plane, color), *self.get_projection(c2, plane, color)
        c1, c2 = obj.intersection(
            ag.Plane(obj.center, obj.vector, ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1)))
        c3, c4 = obj.intersection(
            ag.Plane(obj.center, obj.vector, ag.Vector(1, 0, 0) if plane == 'xy' else ag.Vector(1, 0, 0)))
        return *circles, *self.get_projection(c1, plane, color), *self.get_projection(c2, plane, color), \
               *self.get_projection(c3, plane, color), *self.get_projection(c4, plane, color)

    def spline_projections(self, obj, plane, color):
        res = []
        for i in range(1, len(obj.array)):
            pr = self.get_projection(obj.array[i][1], plane, color)
            if isinstance(pr, (tuple, list)):
                res.extend(list(pr))
            else:
                res.append(pr)
        return res

    def rotation_surface_projections(self, obj, plane, color):
        res = self.get_projection(ag.Circle(obj.center1, obj.radius1, obj.vector), plane, color), \
              self.get_projection(ag.Circle(obj.center2, obj.radius2, obj.vector), plane, color), \
              self.get_projection(obj.spline1, plane, color), self.get_projection(obj.spline2, plane, color)
        return unpack_inner_tuples(res)

    def get_point(self, obj, plane, color):
        return ScreenPoint2(self.plot, *self.convert_ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                            color)

    def convert_ag_coordinate_to_screen_coordinate(self, x, y=None, z=None, plane='xy'):
        if plane == 'xy':
            return int(self.axis.rp[0] + self.camera_pos[0] - x * self.zoom), int(self.axis.lp[1] + y * self.zoom)
        return int(self.axis.rp[0] + self.camera_pos[0] - x * self.zoom), int(self.axis.lp[1] - z * self.zoom)

    def convert_screen_x_to_ag_x(self, x):
        return (self.camera_pos[0] + self.axis.rp[0] - x) / self.zoom

    def convert_screen_y_to_ag_y(self, y):
        return (y - self.axis.lp[1]) / self.zoom

    def convert_screen_y_to_ag_z(self, z):
        return (self.axis.lp[1] - z) / self.zoom


def unpack_inner_tuples(tpl):
    new = list()
    for el in tpl:
        if isinstance(el, (tuple, list)):
            new.extend(el)
        else:
            new.append(el)
    return new
