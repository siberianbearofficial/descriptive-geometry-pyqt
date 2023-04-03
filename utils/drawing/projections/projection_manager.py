import core.angem as ag
from utils.drawing.projections.screen_point import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.screen_segment import ScreenSegment
from utils.drawing.projections.screen_circle import ScreenCircle
from utils.color import *
import math
from PyQt5.QtCore import Qt


class ProjectionManager:

    def __init__(self, plot):
        self.plot = plot
        self.axis = plot.axis
        self.zoom = 1
        self.camera_pos = (0, 0)

    def get_projection(self, obj, color, **kwargs):
        if isinstance(obj, ag.Point):
            p_xy = self.point_projections(obj, 'xy', color)
            p_xz = self.point_projections(obj, 'xz', color)
            if kwargs.get('draw_cl', False):
                return p_xy, p_xz, ScreenSegment(self.plot, p_xy, p_xz, color=CONNECT_LINE_COLOR, thickness=1,
                                                 line_type=Qt.DashLine)
            return self.point_projections(obj, 'xy', color), self.point_projections(obj, 'xz', color)

        elif isinstance(obj, ag.Circle):
            return self.circle_projections(obj, color)

        elif isinstance(obj, ag.Arc):
            return self.arc_projections(obj, color)

        elif isinstance(obj, ag.Segment):
            p1_xy = self.point_projections(obj.p1, 'xy', color)
            p2_xy = self.point_projections(obj.p2, 'xy', color)
            p1_xz = self.point_projections(obj.p1, 'xz', color)
            p2_xz = self.point_projections(obj.p2, 'xz', color)
            if kwargs.get('draw_cl', False):
                return (self.segment_projections(obj, 'xy', color), p1_xy, p2_xy), \
                       (self.segment_projections(obj, 'xz', color), p1_xz, p2_xz), \
                       (ScreenSegment(self.plot, p1_xy, p1_xz, color=CONNECT_LINE_COLOR, thickness=1, line_type=Qt.DashLine),
                        ScreenSegment(self.plot, p2_xy, p2_xz, color=CONNECT_LINE_COLOR, thickness=1, line_type=Qt.DashLine))
            return (self.segment_projections(obj, 'xy', color), p1_xy, p2_xy), \
                   (self.segment_projections(obj, 'xz', color), p1_xz, p2_xz)

        elif isinstance(obj, ag.Plane):
            if kwargs.get('draw_3p', False) and kwargs.get('draw_cl', False):
                p_xy = self.plane_projections(obj, 'xy', color, draw_3p=kwargs.get('draw_3p', False))
                p_xz = self.plane_projections(obj, 'xz', color, draw_3p=kwargs.get('draw_3p', False))
                return p_xy, p_xz, \
                       (ScreenSegment(self.plot, p_xy[3], p_xz[3], color=CONNECT_LINE_COLOR, thickness=1, line_type=Qt.DashLine),
                        ScreenSegment(self.plot, p_xy[4], p_xz[4], color=CONNECT_LINE_COLOR, thickness=1, line_type=Qt.DashLine),
                        ScreenSegment(self.plot, p_xy[5], p_xz[5], color=CONNECT_LINE_COLOR, thickness=1, line_type=Qt.DashLine))
            return self.plane_projections(obj, 'xy', color, draw_3p=kwargs.get('draw_3p', False)), \
                   self.plane_projections(obj, 'xz', color, draw_3p=kwargs.get('draw_3p', False))

        elif isinstance(obj, ag.Line):
            return self.line_projections(obj, 'xy', color), self.line_projections(obj, 'xz', color)

        elif isinstance(obj, ag.Ellipse):
            return self.ellipse_projections(obj, 'xy', color), self.ellipse_projections(obj, 'xz', color)

        elif isinstance(obj, ag.Sphere):
            return self.sphere_projections(obj, 'xy', color), self.sphere_projections(obj, 'xz', color)

        elif isinstance(obj, ag.Cylinder):
            return self.cylinder_projections(obj, color)

        elif isinstance(obj, ag.Cone):
            return self.cone_projections(obj, color)

        elif isinstance(obj, ag.RotationSurface):
            return self.rotation_surface_projections(obj, color)

        elif isinstance(obj, ag.Tor):
            return self.tor_projections(obj, 'xy', color), self.tor_projections(obj, 'xz', color)

        elif isinstance(obj, ag.Spline) or isinstance(obj, ag.Spline3D):
            return self.spline_projections(obj, color)

        elif isinstance(obj, ag.IntersectionObject):
            l1, l2, l3 = [], [], []
            for el in obj.objects:
                pr = self.get_projection(el, color)
                l1.append(pr[0])
                l2.append(pr[1])
                if len(pr) == 3:
                    l3.append(pr[2])
            return unpack_inner_tuples(l1), unpack_inner_tuples(l2), unpack_inner_tuples(l3)

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

    def plane_projections(self, obj, plane, color, draw_3p=False):
        if draw_3p:
            p1 = self.point_projections(obj.point, plane, color)
            p2 = self.point_projections(obj.point + obj.vector1, plane, color)
            p3 = self.point_projections(obj.point + obj.vector2, plane, color)
            return ScreenSegment(self.plot, p1.tuple(), p2.tuple(), color), \
                   ScreenSegment(self.plot, p2.tuple(), p3.tuple(), color), \
                   ScreenSegment(self.plot, p3.tuple(), p1.tuple(), color), p1, p2, p3
        if plane == 'xy':
            return self.line_projections(obj.trace_xy(), plane, color)
        return self.line_projections(obj.trace_xz(), plane, color)

    def circle_projections(self, obj, color):
        if obj.radius == 0:
            return self.point_projections(obj.center, 'xy', color), self.point_projections(obj.center, 'xz', color)
        if obj.normal.x == 0 and obj.normal.y == 0:
            center_xy = self.point_projections(obj.center, 'xy', color)
            center_xz = self.point_projections(obj.center, 'xz', color)
            return ScreenCircle(self.plot, center_xy, obj.radius * self.zoom,
                                color), \
                   ScreenSegment(self.plot, (center_xz.x + obj.radius * self.zoom, center_xz.y),
                                 (center_xz.x - obj.radius * self.zoom, center_xz.y), color=color)
        if obj.normal.x == 0 and obj.normal.z == 0:
            center_xy = self.point_projections(obj.center, 'xy', color)
            center_xz = self.point_projections(obj.center, 'xz', color)
            return ScreenSegment(self.plot, (center_xy.x + obj.radius * self.zoom, center_xy.y),
                                 (center_xy.x - obj.radius * self.zoom, center_xy.y), color=color), \
                   ScreenCircle(self.plot, center_xz, obj.radius * self.zoom,
                                color)

        # if obj.normal * (ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)) == 0:
        #     point1, point2 = obj.intersection(
        #         ag.Line(obj.center, obj.normal & (ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0))))
        #     return self.segment_projections(ag.Segment(point1, point2), plane, color),

        vector_sin = obj.normal & (obj.normal + ag.Vector(2, 1, 1))
        vector_sin = vector_sin * (obj.radius / abs(vector_sin))
        vector_cos = obj.normal & vector_sin
        vector_cos = vector_cos * (obj.radius / abs(vector_cos))
        step = 1 / self.zoom / obj.radius
        x, lst_xy, lst_xz = 0, [], []
        while x < 1.57:
            s, c = math.sin(x), math.cos(x)
            lst_xy.append(self.get_point(obj.center + vector_sin * s + vector_cos * c, 'xy', color))
            lst_xy.append(self.get_point(obj.center + -vector_sin * s + vector_cos * c, 'xy', color))
            lst_xy.append(self.get_point(obj.center + vector_sin * s + -vector_cos * c, 'xy', color))
            lst_xy.append(self.get_point(obj.center + -vector_sin * s + -vector_cos * c, 'xy', color))

            lst_xz.append(self.get_point(obj.center + vector_sin * s + vector_cos * c, 'xz', color))
            lst_xz.append(self.get_point(obj.center + -vector_sin * s + vector_cos * c, 'xz', color))
            lst_xz.append(self.get_point(obj.center + vector_sin * s + -vector_cos * c, 'xz', color))
            lst_xz.append(self.get_point(obj.center + -vector_sin * s + -vector_cos * c, 'xz', color))
            x += step
        return tuple(lst_xy), tuple(lst_xz)

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
        return ScreenCircle(self.plot, self.point_projections(obj.center, plane, color), obj.radius * self.zoom, color)

    def cylinder_projections(self, obj, color):
        v_xy = ag.Vector(0, 0, 1)
        v_xz = ag.Vector(0, 1, 0)
        circle1 = self.circle_projections(ag.Circle(obj.center1, obj.radius, obj.vector), color)
        circle2 = self.circle_projections(ag.Circle(obj.center2, obj.radius, obj.vector), color)
        if obj.vector | v_xy:
            res_xy = circle1[0], circle2[0]
        else:
            res_xy = circle1[0], circle2[0], self.segment_projections(
                ag.Segment(obj.center1 + (obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy))),
                           obj.center2 + (obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy)))),
                'xy', color), self.segment_projections(
                ag.Segment(obj.center1 + -(obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy))),
                           obj.center2 + -(obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy)))),
                'xy', color)
        if obj.vector | v_xz:
            res_xz = circle1[1], circle2[1]
        else:
            res_xz = circle1[1], circle2[1], self.segment_projections(
                ag.Segment(obj.center1 + (obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz))),
                           obj.center2 + (obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz)))),
                'xz', color), self.segment_projections(
                ag.Segment(obj.center1 + -(obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz))),
                           obj.center2 + -(obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz)))),
                'xz', color)
        return unpack_inner_tuples(res_xy), unpack_inner_tuples(res_xz)

    def cone_projections(self, obj, color):
        v_xy = ag.Vector(0, 0, 1)
        v_xz = ag.Vector(0, 1, 0)
        circle1 = self.circle_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), color)
        circle2 = self.circle_projections(ag.Circle(obj.center2, obj.radius2, obj.vector), color)
        if obj.vector | v_xy:
            res_xy = circle1[0], circle2[0]
        else:
            res_xy = circle1[0], circle2[0], self.segment_projections(
                ag.Segment(obj.center1 + (obj.vector & v_xy * (obj.radius1 / abs(obj.vector & v_xy))),
                           obj.center2 + (obj.vector & v_xy * (obj.radius2 / abs(obj.vector & v_xy)))),
                'xy', color), self.segment_projections(
                ag.Segment(obj.center1 + -(obj.vector & v_xy * (obj.radius1 / abs(obj.vector & v_xy))),
                           obj.center2 + -(obj.vector & v_xy * (obj.radius2 / abs(obj.vector & v_xy)))),
                'xy', color)
        if obj.vector | v_xz:
            res_xz = circle1[1], circle2[1]
        else:
            res_xz = circle1[1], circle2[1], self.segment_projections(
                ag.Segment(obj.center1 + (obj.vector & v_xz * (obj.radius1 / abs(obj.vector & v_xz))),
                           obj.center2 + (obj.vector & v_xz * (obj.radius2 / abs(obj.vector & v_xz)))),
                'xz', color), self.segment_projections(
                ag.Segment(obj.center1 + -(obj.vector & v_xz * (obj.radius1 / abs(obj.vector & v_xz))),
                           obj.center2 + -(obj.vector & v_xz * (obj.radius2 / abs(obj.vector & v_xz)))),
                'xz', color)
        return unpack_inner_tuples(res_xy), unpack_inner_tuples(res_xz)

    def arc_projections(self, obj, color):
        step = 1 / self.zoom / obj.radius
        x, lst1, lst2 = 0, [], []
        if obj.angle >= 0:
            while x < obj.angle:
                s, c = math.sin(x), math.cos(x)
                lst1.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, 'xy', color))
                lst2.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, 'xz', color))
                x += step
        else:
            while x > obj.angle:
                s, c = math.sin(x), math.cos(x)
                lst1.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, 'xy', color))
                lst2.append(self.get_point(obj.center + obj.vector_sin * s + obj.vector_cos * c, 'xz', color))
                x -= step
        return tuple(lst1), tuple(lst2)

    def tor_projections(self, obj, plane, color):
        if obj.tube_radius > obj.radius:
            circles = *self.circle_projections(ag.Circle(obj.center, obj.radius + obj.tube_radius, obj.vector), plane,
                                               color), \
                      *self.circle_projections(ag.Circle(obj.center + obj.vector * (obj.tube_radius / abs(obj.vector)),
                                                         obj.radius, obj.vector), plane, color), \
                      *self.circle_projections(ag.Circle(obj.center + obj.vector * (-obj.tube_radius / abs(obj.vector)),
                                                         obj.radius, obj.vector), plane, color)
        else:
            circles = *self.circle_projections(ag.Circle(obj.center, obj.radius + obj.tube_radius, obj.vector), plane,
                                               color), \
                      *self.circle_projections(ag.Circle(obj.center, obj.radius - obj.tube_radius, obj.vector), plane,
                                               color), \
                      *self.circle_projections(ag.Circle(obj.center + obj.vector * (obj.tube_radius / abs(obj.vector)),
                                                         obj.radius, obj.vector), plane, color), \
                      *self.circle_projections(ag.Circle(obj.center + obj.vector * (-obj.tube_radius / abs(obj.vector)),
                                                         obj.radius, obj.vector), plane, color)
        if (obj.vector * ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)) == 0:
            c1, c2 = obj.intersection(ag.Plane(ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1),
                                               obj.center))
            return *circles, *self.circle_projections(c1, plane, color), *self.circle_projections(c2, plane, color)
        c1, c2 = obj.intersection(
            ag.Plane(obj.center, obj.vector, ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1)))
        c3, c4 = obj.intersection(
            ag.Plane(obj.center, obj.vector, ag.Vector(1, 0, 0) if plane == 'xy' else ag.Vector(1, 0, 0)))
        return *circles, *self.circle_projections(c1, plane, color), *self.circle_projections(c2, plane, color), \
               *self.circle_projections(c3, plane, color), *self.circle_projections(c4, plane, color)

    def spline_projections(self, obj, color):
        res1 = []
        res2 = []
        for i in range(1, len(obj.array)):
            pr = self.arc_projections(obj.array[i][1], color)
            if isinstance(pr[0], (tuple, list)):
                res1.extend(list(pr[0]))
            else:
                res1.append(pr[0])
            if isinstance(pr[1], (tuple, list)):
                res2.extend(list(pr[1]))
            else:
                res2.append(pr[1])
        return res1, res2

    def rotation_surface_projections(self, obj, color):
        res1, res2 = zip(self.circle_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), color),
                         self.circle_projections(ag.Circle(obj.center2, obj.radius2, obj.vector), color),
                         self.spline_projections(obj.spline1, color), self.spline_projections(obj.spline2, color))
        # res = self.circle_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), color), \
        #       self.circle_projections(ag.Circle(obj.center2, obj.radius2, obj.vector), color), \
        #       self.spline_projections(obj.spline1, color), self.spline_projections(obj.spline2, color)
        return unpack_inner_tuples(res1), unpack_inner_tuples(res2)

    def get_point(self, obj, plane, color):
        return ThinScreenPoint(self.plot, *self.convert_ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                               color)

    def convert_ag_coordinate_to_screen_coordinate(self, x, y=None, z=None, plane='xy'):
        if plane == 'xy':
            return self.axis.rp[0] + self.camera_pos[0] - x * self.zoom, self.axis.lp[1] + y * self.zoom
        return self.axis.rp[0] + self.camera_pos[0] - x * self.zoom, self.axis.lp[1] - z * self.zoom

    def ag_x_to_screen_x(self, x):
        return self.axis.rp[0] + self.camera_pos[0] - x * self.zoom

    def ag_y_to_screen_y(self, y):
        return self.axis.lp[1] + y * self.zoom

    def ag_z_to_screen_y(self, z):
        return self.axis.lp[1] - z * self.zoom

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
