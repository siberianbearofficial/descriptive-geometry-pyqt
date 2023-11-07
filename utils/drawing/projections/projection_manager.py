import math

from PyQt6.QtCore import Qt

import core.angem as ag
from core.config import CANVASS_X, SCALE, CANVASS_Y
from utils.drawing.projections.screen_point import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.screen_segment import ScreenSegment

XY = 0
XZ = 1


def get_projection(obj, color, thickness, **kwargs):
    if isinstance(obj, ag.Point):
        p_xy = point_projections(obj, 'xy', color, thickness)
        p_xz = point_projections(obj, 'xz', color, thickness)
        return p_xy, p_xz, ScreenSegment(p_xy, p_xz, line_type=Qt.PenStyle.DashLine, thickness=1)

    elif isinstance(obj, ag.Segment):
        p1_xy = point_projections(obj.p1, 'xy', color, thickness)
        p2_xy = point_projections(obj.p2, 'xy', color, thickness)
        p1_xz = point_projections(obj.p1, 'xz', color, thickness)
        p2_xz = point_projections(obj.p2, 'xz', color, thickness)
        return (segment_projections(obj, 'xy', color, thickness), p1_xy, p2_xy), \
            (segment_projections(obj, 'xz', color, thickness), p1_xz, p2_xz), \
            (ScreenSegment(p1_xy, p1_xz, line_type=Qt.PenStyle.DashLine, thickness=1),
             ScreenSegment(p2_xy, p2_xz, line_type=Qt.PenStyle.DashLine, thickness=1))

    elif isinstance(obj, ag.Plane):
        return plane_projections(obj, color, thickness)

    elif isinstance(obj, ag.Line):
        return line_projections(obj, 'xy', color, thickness), \
            line_projections(obj, 'xz', color, thickness), []

    elif isinstance(obj, ag.Polygon2D):
        return polygon_2d_projections(obj, color, thickness)

    elif isinstance(obj, ag.Cylinder):
        return cylinder_projections(obj, color, thickness)

    elif isinstance(obj, ag.Cone):
        return cone_projections(obj, color, thickness)

    elif isinstance(obj, ag.Sphere):
        return sphere_projections(obj, color, thickness)

    elif isinstance(obj, ag.Tor):
        return tor_projections(obj, color, thickness)

    elif isinstance(obj, ag.IntersectionLine):
        return intersection_line_projections(obj, color, thickness)

    raise TypeError(f"cannot find projections to {obj.__class__.__name__}")

    # elif isinstance(obj, ag.IntersectionObject):
    #     l1, l2, l3 = [], [], []
    #     for el in obj.objects:
    #         pr = get_projection(el, color, thickness)
    #         l1.append(pr[0])
    #         l2.append(pr[1])
    #         if len(pr) == 3:
    #             l3.append(pr[2])
    #     return unpack_inner_tuples(l1), unpack_inner_tuples(l2), unpack_inner_tuples(l3)


def point_projections(obj, plane, color, thickness):
    return ScreenPoint(*ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                       color, thickness)


def segment_projections(obj, plane, color, thickness):
    p1 = ScreenPoint(*ag_coordinate_to_screen_coordinate(obj.p1.x, obj.p1.y, obj.p1.z, plane),
                     color, thickness)
    p2 = ScreenPoint(*ag_coordinate_to_screen_coordinate(obj.p2.x, obj.p2.y, obj.p2.z, plane),
                     color, thickness)

    return ScreenSegment(p1, p2, color, thickness)


def line_projections(obj, plane, color, thickness=1):
    if plane == 'xy':
        segment = obj.cut_by_y(0, CANVASS_Y // 2)
    else:
        segment = obj.cut_by_z(0, CANVASS_Y // 2)
    return segment_projections(segment, plane, color, thickness)


def plane_projections(obj, color, thickness, draw_3p=False):
    if draw_3p:
        return [], [], []
        # p1 = point_projections(obj.point, plane, color, thickness)
        # p2 = point_projections(obj.point + obj.vector1, plane, color, thickness)
        # p3 = point_projections(obj.point + obj.vector2, plane, color, thickness)
        # return ScreenSegment(tuple(p1), tuple(p2), color, thickness), \
        #     ScreenSegment(tuple(p2), tuple(p3), color, thickness), \
        #     ScreenSegment(tuple(p3), tuple(p1), color, thickness), p1, p2, p3

    return line_projections(obj.trace_xy(), 'xy', color, thickness), \
        line_projections(obj.trace_xz(), 'xz', color, thickness), []


def intersection_line_projections(obj: ag.IntersectionLine, color, thickness):
    return [segment_projections(el, 'xy', color, thickness) for el in obj.segments], \
        [segment_projections(el, 'xz', color, thickness) for el in obj.segments], []


def polygon_2d_projections(obj: ag.Polygon2D, color, thickness):
    lst_xy = []
    lst_xz = []
    for p1, p2 in obj.get_pairs():
        segment = ag.Segment(p1, p2)
        lst_xy.append(segment_projections(segment, 'xy', color, thickness))
        lst_xz.append(segment_projections(segment, 'xz', color, thickness))
    return lst_xy, lst_xz, tuple()


def sphere_projections(obj: ag.Sphere, color, thickness):
    # xy_proj = []
    # xz_proj = []
    # for el in obj.polygons:
    #     xy, xz, _ = polygon_2d_projections(el, color, thickness)
    #     xy_proj.extend(xy)
    #     xz_proj.extend(xz)
    # return xy_proj, xz_proj, tuple()
    xy = polygon_2d_projections(ag.Circle(obj.center, obj.radius, ag.Vector(0, 0, 1)), color, thickness)[0]
    xz = polygon_2d_projections(ag.Circle(obj.center, obj.radius, ag.Vector(0, 1, 0)), color, thickness)[1]
    return xy, xz, tuple()


def cylinder_projections(obj, color, thickness):
    v_xy = ag.Vector(0, 0, 1)
    v_xz = ag.Vector(0, 1, 0)
    circle1 = polygon_2d_projections(ag.Circle(obj.center1, obj.radius, obj.vector), color, thickness)
    circle2 = polygon_2d_projections(ag.Circle(obj.center2, obj.radius, obj.vector), color, thickness)
    if obj.vector | v_xy:
        res_xy = circle1[0], circle2[0]
    else:
        res_xy = circle1[0], circle2[0], segment_projections(
            ag.Segment(obj.center1 + (obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy))),
                       obj.center2 + (obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy)))),
            'xy', color, thickness), segment_projections(
            ag.Segment(obj.center1 + -(obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy))),
                       obj.center2 + -(obj.vector & v_xy * (obj.radius / abs(obj.vector & v_xy)))),
            'xy', color, thickness)
    if obj.vector | v_xz:
        res_xz = circle1[1], circle2[1]
    else:
        res_xz = circle1[1], circle2[1], segment_projections(
            ag.Segment(obj.center1 + (obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz))),
                       obj.center2 + (obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz)))),
            'xz', color, thickness), segment_projections(
            ag.Segment(obj.center1 + -(obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz))),
                       obj.center2 + -(obj.vector & v_xz * (obj.radius / abs(obj.vector & v_xz)))),
            'xz', color, thickness)
    return unpack_inner_tuples(res_xy), unpack_inner_tuples(res_xz), tuple()


def cone_projections(obj, color, thickness):
    v_xy = ag.Vector(0, 0, 1)
    v_xz = ag.Vector(0, 1, 0)
    circle1 = polygon_2d_projections(ag.Circle(obj.center1, obj.radius1, obj.vector), color, thickness)
    circle2 = polygon_2d_projections(ag.Circle(obj.center2, obj.radius2, obj.vector), color, thickness)
    if obj.vector | v_xy:
        res_xy = circle1[0], circle2[0]
    else:
        res_xy = circle1[0], circle2[0], segment_projections(
            ag.Segment(obj.center1 + (obj.vector & v_xy * (obj.radius1 / abs(obj.vector & v_xy))),
                       obj.center2 + (obj.vector & v_xy * (obj.radius2 / abs(obj.vector & v_xy)))),
            'xy', color, thickness), segment_projections(
            ag.Segment(obj.center1 + -(obj.vector & v_xy * (obj.radius1 / abs(obj.vector & v_xy))),
                       obj.center2 + -(obj.vector & v_xy * (obj.radius2 / abs(obj.vector & v_xy)))),
            'xy', color, thickness)
    if obj.vector | v_xz:
        res_xz = circle1[1], circle2[1]
    else:
        res_xz = circle1[1], circle2[1], segment_projections(
            ag.Segment(obj.center1 + (obj.vector & v_xz * (obj.radius1 / abs(obj.vector & v_xz))),
                       obj.center2 + (obj.vector & v_xz * (obj.radius2 / abs(obj.vector & v_xz)))),
            'xz', color, thickness), segment_projections(
            ag.Segment(obj.center1 + -(obj.vector & v_xz * (obj.radius1 / abs(obj.vector & v_xz))),
                       obj.center2 + -(obj.vector & v_xz * (obj.radius2 / abs(obj.vector & v_xz)))),
            'xz', color, thickness)
    return unpack_inner_tuples(res_xy), unpack_inner_tuples(res_xz), []


def tor_projections(obj, color, thickness):
    xy_proj, xz_proj = [], []

    for el in obj.polygons:
        xy, xz, _ = polygon_2d_projections(el, color, 1)
        xy_proj.extend(xy)
        xz_proj.extend(xz)

    # xy, xz, _ = polygon_2d_projections(ag.Circle(obj.center, obj.radius + obj.tube_radius, obj.vector),
    #                                    color, thickness)
    # xy_proj.extend(xy)
    # xz_proj.extend(xz)
    # xy, xz, _ = polygon_2d_projections(ag.Circle(obj.center + obj.vector * (obj.tube_radius / abs(obj.vector)),
    #                                              obj.radius, obj.vector), color, thickness)
    # xy_proj.extend(xy)
    # xz_proj.extend(xz)
    # xy, xz, _ = polygon_2d_projections(ag.Circle(obj.center + obj.vector * (-obj.tube_radius / abs(obj.vector)),
    #                                              obj.radius, obj.vector), color, thickness)
    # xy_proj.extend(xy)
    # xz_proj.extend(xz)
    # if obj.tube_radius <= obj.radius:
    #     xy, xz, _ = polygon_2d_projections(ag.Circle(obj.center, obj.radius - obj.tube_radius, obj.vector),
    #                                        color, thickness)
    #     xy_proj.extend(xy)
    #     xz_proj.extend(xz)

    # if (obj.vector * ag.Vector(0, 0, 1) if plane == 'xy' else ag.Vector(0, 1, 0)) == 0:
    #     c1, c2 = obj.intersection(ag.Plane(ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1),
    #                                        obj.center))
    #     return *circles, *polygon_2d_projections(c1, color, thickness), *polygon_2d_projections(c2, color,
    #                                                                                             thickness)
    # c1, c2 = obj.intersection(
    #     ag.Plane(obj.center, obj.vector, ag.Vector(0, 1, 0) if plane == 'xy' else ag.Vector(0, 0, 1)))
    # c3, c4 = obj.intersection(
    #     ag.Plane(obj.center, obj.vector, ag.Vector(1, 0, 0) if plane == 'xy' else ag.Vector(1, 0, 0)))
    # return *circles, *polygon_2d_projections(c1, color, thickness), *polygon_2d_projections(c2, color, thickness), \
    #     *polygon_2d_projections(c3, color, thickness), *polygon_2d_projections(c4, color, thickness)
    return xy_proj, xz_proj, []


def get_point(obj, plane, color, thickness):
    return ThinScreenPoint(*ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                           color, thickness)


def ag_coordinate_to_screen_coordinate(x, y=None, z=None, plane='xy') -> tuple[int, int]:
    if plane == 'xy':
        return ag_x_to_screen_x(x), ag_y_to_screen_y(y)
    return ag_x_to_screen_x(x), ag_z_to_screen_y(z)


def ag_x_to_screen_x(x):
    return CANVASS_X // 2 - x * SCALE


def ag_y_to_screen_y(y):
    return CANVASS_Y // 2 + y * SCALE


def ag_z_to_screen_y(z):
    return CANVASS_Y // 2 - z * SCALE


def screen_x_to_ag_x(x):
    return (CANVASS_X // 2 - x) / SCALE


def screen_y_to_ag_y(y):
    return (y - CANVASS_Y // 2) / SCALE


def screen_y_to_ag_z(z):
    return (CANVASS_Y // 2 - z) / SCALE


def unpack_inner_tuples(tpl):
    new = list()
    for el in tpl:
        if isinstance(el, (tuple, list)):
            new.extend(el)
        else:
            new.append(el)
    return new
