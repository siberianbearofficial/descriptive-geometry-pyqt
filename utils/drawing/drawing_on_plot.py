from time import sleep
from typing import Literal

from core.config import CANVASS_Y
from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
import core.angem as ag
from PyQt6.QtCore import Qt, QThread, QPoint

import utils.drawing.projections.projection_manager as projections
from utils.drawing.snap import SnapManager
from utils.objects.general_object import GeneralObject

SEP = ','


def select_screen_point(plot, func, step, kwargs, plane, x=None, c=None, objects=tuple(), object_func=None,
                        final_func=None, draw_point=True):
    if plane == 'xy':
        if x is None:
            y, z = c, c
        else:
            y, z = None, c
    elif x is None:
        y, z = c, c
    else:
        y, z = c, None

    def mouse_move(pos):
        pos = plot.sm.get_snap((pos.x(), pos.y()), plane, x=x, y=y, z=z)
        if c is not None and x is not None:
            if object_func:
                if draw_point:
                    plot.update(ScreenSegment((x, c), pos, color=plot.cl_color, thickness=1), *object_func(pos),
                                *objects,
                                ScreenPoint(*pos, color=plot.draw_color))
                else:
                    plot.update(ScreenSegment((x, c), pos, color=plot.cl_color, thickness=1), *object_func(pos),
                                *objects)
            else:
                plot.update(ScreenSegment((x, c), pos, color=plot.cl_color, thickness=1), *objects,
                            ScreenPoint(*pos, color=plot.draw_color))

        elif object_func:
            if draw_point:
                plot.update(*objects, ScreenPoint(*pos, color=plot.draw_color), *object_func(pos))
            else:
                plot.update(*objects, *object_func(pos))
        else:
            plot.update(*objects, ScreenPoint(*pos, color=plot.draw_color))

    def mouse_left(pos):
        pos = plot.sm.get_snap((pos.x(), pos.y()), plane, x=x, y=y, z=z)
        if final_func:
            final_func(pos)
        else:
            func(plot, step + 1, **kwargs, x=pos[0], c=pos[1])

    plot.mouse_move = mouse_move
    plot.mouse_left = mouse_left
    plot.mouse_right = lambda pos: plot.end()


def select_object(plot, func, step, kwargs, types=None, final_func=None):
    def mouse_move(pos):
        selected_object = None
        pos = pos.x(), pos.y()
        for obj in plot.objects:
            if types and obj.general_object.ag_object.__class__ not in types:
                continue
            for el in obj.xy_projection:
                if isinstance(el, ScreenPoint) and distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                if isinstance(el, ThinScreenPoint) and distance(pos, el.tuple()) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenSegment) and distance(pos, nearest_point(pos, el)) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenCircle) and abs(distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
            for el in obj.xz_projection:
                if isinstance(el, ScreenPoint) and distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                if isinstance(el, ThinScreenPoint) and distance(pos, el.tuple()) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenSegment) and distance(pos, nearest_point(pos, el)) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenCircle) and abs(distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
        if selected_object:
            plot.update(selected_object, selected=2)
        else:
            plot.update()

    def mouse_left(pos):
        selected_object = None
        pos = pos.x(), pos.y()
        for obj in plot.objects:
            for el in obj.xy_projection:
                if isinstance(el, ScreenPoint) and distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                if isinstance(el, ThinScreenPoint) and distance(pos, el.tuple()) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenSegment) and distance(pos, nearest_point(pos, el)) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenCircle) and abs(distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
            for el in obj.xz_projection:
                if isinstance(el, ScreenPoint) and distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                if isinstance(el, ThinScreenPoint) and distance(pos, el.tuple()) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenSegment) and distance(pos, nearest_point(pos, el)) <= 3:
                    selected_object = obj
                if isinstance(el, ScreenCircle) and abs(distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
        if selected_object:
            if final_func:
                final_func(selected_object)
            else:
                func(plot, step + 1, **kwargs, obj=selected_object)

    plot.mouse_move = mouse_move
    plot.mouse_left = mouse_left
    plot.mouse_right = lambda pos: plot.end()


def cmd_command(plot, args_number, func):
    def command(s):
        print(s)
        if s.count(SEP) == args_number - 1:
            func(*map(eval, s.split(SEP)))

    # plot.cmd_command = command
    # plot.setCmdStatus.emit(True)


def convert_point(plot, x, y, z):
    if not isinstance(y, int) and not isinstance(y, float):
        x = plot.plot_x_to_ag_x(x)
        z = plot.plot_y_to_ag_z(z)
        return x, y(x, z), z
    if not isinstance(z, int) and not isinstance(z, float):
        x = plot.plot_x_to_ag_x(x)
        y = plot.plot_y_to_ag_y(y)
        return x, y, z(x, y)
    return plot.plot_x_to_ag_x(x), plot.plot_y_to_ag_y(y), plot.plot_y_to_ag_z(z)


def create_point(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_point, 1, kwargs, 'xy')
        cmd_command(plot, 3, lambda x, y, z: plot.add_object(ag.Point(x, y, z), end=True))
    elif step == 2:
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_point, 2, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                            final_func=lambda pos: plot.add_object(ag.Point(
                                *convert_point(plot, kwargs['x'], kwargs['c'], pos[1])), end=True))


def create_segment(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_segment, 1, kwargs, 'xy')
        cmd_command(plot, 3, lambda x, y, z: create_segment(
            plot, 3, x1=projections.ag_x_to_screen_x(x), y1=projections.ag_y_to_screen_y(y),
            c=projections.ag_y_to_screen_z(z)))
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_segment, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(plot, create_segment, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
        cmd_command(plot, 3, lambda x, y, z: plot.add_object(ag.Segment(ag.Point(
            *convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])), ag.Point(x, y, z)), end=True))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        s2 = ScreenSegment(a1, b1, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(
            plot, create_segment, 3, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                      'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Segment(
                ag.Point(*convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])),
                ag.Point(*convert_point(plot, kwargs['x2'], kwargs['y2'], pos[1]))
            ), end=True, draw_cl=True))


def create_line(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_line, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_line, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(plot, create_line, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        s2 = ScreenSegment(a1, b1, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(
            plot, create_line, 3, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                   'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Line(
                ag.Point(*convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])),
                ag.Point(*convert_point(plot, kwargs['x2'], kwargs['y2'], pos[1]))
            ), end=True))


def create_plane(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_plane, 1, kwargs, 'xy', c=plot.axis.lp[1])
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], plot.axis.lp[1], color=plot.draw_color)
        select_screen_point(plot, create_plane, 2, {'x0': kwargs['x']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (
                                ScreenSegment((kwargs['x'], plot.axis.lp[1]), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x0'], plot.axis.lp[1], color=plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(
            plot, create_plane, 3, {'x0': kwargs['x0'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xz', objects=(a1, a2, s1),
            object_func=lambda pos: (ScreenSegment((kwargs['x0'], plot.axis.lp[1]), pos, plot.draw_color),),
            final_func=lambda pos: plot.add_object(
                ag.Plane(ag.Vector(ag.Point(plot.plot_x_to_ag_x(kwargs['x0']), 0, 0),
                                   ag.Point(plot.plot_x_to_ag_x(kwargs['x']),
                                            plot.plot_y_to_ag_y(kwargs['c']))) & ag.Vector(
                    ag.Point(plot.plot_x_to_ag_x(kwargs['x0']), 0, 0),
                    ag.Point(plot.plot_x_to_ag_x(pos[0]), 0, plot.plot_y_to_ag_z(pos[1])
                             )),
                         ag.Point(plot.plot_x_to_ag_x(kwargs['x0']), 0, 0)), end=True))


def create_cylinder(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_cylinder, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_cylinder, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(plot, create_cylinder, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        s2 = ScreenSegment(a1, b1, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(
            plot, create_cylinder, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                       'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 5:
        p1 = ag.Point(plot.plot_x_to_ag_x(kwargs['x1']), plot.plot_y_to_ag_y(kwargs['y1']),
                      plot.plot_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.plot_x_to_ag_x(kwargs['x2']), plot.plot_y_to_ag_y(kwargs['y2']),
                      plot.plot_y_to_ag_z(kwargs['c']))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        select_screen_point(
            plot, create_cylinder, 5, dict(), 'xy',
            object_func=lambda pos: (GeneralObject(ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                plane.z(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]))
            ))), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                plane.z(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]))
            ))), end=True))


def create_perpendicular_segment(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment, line or plane')
        select_object(plot, create_perpendicular_segment, 1, kwargs, (ag.Line, ag.Plane, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_perpendicular_segment, 2, {'obj': kwargs['obj'].general_object.ag_object},
                            'xy')
    elif step == 3:
        if isinstance(kwargs['obj'], ag.Segment):
            kwargs['obj'] = ag.Line(kwargs['obj'].p1, kwargs['obj'].p2)
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        if isinstance(kwargs['obj'], ag.Line):
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Segment(ag.Point(
                    plot.plot_x_to_ag_x(kwargs['x']),
                    plot.plot_y_to_ag_y(kwargs['c']),
                    plot.plot_y_to_ag_z(pos[1])),
                    ag.Line(ag.Point(
                        plot.plot_x_to_ag_x(kwargs['x']),
                        plot.plot_y_to_ag_y(kwargs['c']),
                        plot.plot_y_to_ag_z(pos[1])),
                        kwargs['obj'].vector & ag.Plane(kwargs['obj'], ag.Point(
                            plot.plot_x_to_ag_x(kwargs['x']),
                            plot.plot_y_to_ag_y(kwargs['c']),
                            plot.plot_y_to_ag_z(pos[1]))).normal).intersection(kwargs['obj'])
                ), end=True))
        else:
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Segment(ag.Point(
                    plot.plot_x_to_ag_x(kwargs['x']),
                    plot.plot_y_to_ag_y(kwargs['c']),
                    plot.plot_y_to_ag_z(pos[1])),
                    ag.Line(ag.Point(
                        plot.plot_x_to_ag_x(kwargs['x']),
                        plot.plot_y_to_ag_y(kwargs['c']),
                        plot.plot_y_to_ag_z(pos[1])),
                        kwargs['obj'].normal).intersection(kwargs['obj'])
                ), end=True, draw_cl=True))


def create_parallel_segment(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment or line')
        select_object(plot, create_parallel_segment, 1, kwargs, (ag.Line, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_parallel_segment, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(
            plot, create_parallel_segment, 3, {'obj': kwargs['obj'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xy', x=kwargs['x'], c=kwargs['c'], objects=(a1,))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], color=plot.draw_color)
        a2 = ScreenPoint(kwargs['x1'], kwargs['c'], color=plot.draw_color)
        s1 = ScreenSegment(a1, a2, color=plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        if isinstance(kwargs['obj'], ag.Segment):
            v = ag.Vector(kwargs['obj'].p1, kwargs['obj'].p2)
        else:
            v = kwargs['obj'].vector
        point = ag.Point(plot.plot_x_to_ag_x(kwargs['x1']), plot.plot_y_to_ag_y(kwargs['y1']),
                         plot.plot_y_to_ag_z(kwargs['c']))
        line = ag.Line(point, v)
        select_screen_point(
            plot, create_parallel_segment, 4, {'obj': kwargs['obj'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xy', objects=(a1, a2, s1),
            object_func=lambda pos: (GeneralObject(ag.Segment(point, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), line.y(x=plot.plot_x_to_ag_x(pos[0])),
                line.z(x=plot.plot_x_to_ag_x(pos[0])))), color=plot.draw_color),), draw_point=False,
            final_func=lambda pos: plot.add_object(ag.Segment(point, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), line.y(x=plot.plot_x_to_ag_x(pos[0])),
                line.z(x=plot.plot_x_to_ag_x(pos[0])))), end=True, draw_cl=True))


def create_perpendicular_line(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment, line or plane')
        select_object(plot, create_perpendicular_line, 1, kwargs, (ag.Line, ag.Plane, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_perpendicular_line, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        if isinstance(kwargs['obj'], ag.Segment):
            kwargs['obj'] = ag.Line(kwargs['obj'].p1, kwargs['obj'].p2)
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        if isinstance(kwargs['obj'], ag.Line):
            select_screen_point(
                plot, create_perpendicular_line, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                    plot.plot_x_to_ag_x(kwargs['x']),
                    plot.plot_y_to_ag_y(kwargs['c']),
                    plot.plot_y_to_ag_z(pos[1])),
                    kwargs['obj'].vector & ag.Plane(kwargs['obj'], ag.Point(
                        plot.plot_x_to_ag_x(kwargs['x']),
                        plot.plot_y_to_ag_y(kwargs['c']),
                        plot.plot_y_to_ag_z(pos[1]))).normal), end=True))
        else:
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                    plot.plot_x_to_ag_x(kwargs['x']), plot.plot_y_to_ag_y(kwargs['c']),
                    plot.plot_y_to_ag_z(pos[1])), kwargs['obj'].normal), end=True))


def create_parallel_line(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment or line')
        select_object(plot, create_parallel_line, 1, kwargs, (ag.Line, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_parallel_line, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        if isinstance(kwargs['obj'], ag.Segment):
            v = ag.Vector(kwargs['obj'].p1, kwargs['obj'].p2)
        else:
            v = kwargs['obj'].vector
        select_screen_point(
            plot, create_parallel_line, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
            object_func=lambda pos: (GeneralObject(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(kwargs['x']),
                plot.plot_y_to_ag_y(kwargs['c']),
                plot.plot_y_to_ag_z(pos[1])), v), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(kwargs['x']),
                plot.plot_y_to_ag_y(kwargs['c']),
                plot.plot_y_to_ag_z(pos[1])), v), end=True))


def create_plane_3p(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_plane_3p, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_plane_3p, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        l1 = ScreenSegment(a1, b1, plot.draw_color)
        select_screen_point(plot, create_plane_3p, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xy', objects=(a1, b1, l1),
                            object_func=lambda pos: (ScreenSegment((kwargs['x1'], kwargs['y1']), pos, plot.draw_color),
                                                     ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color)))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        c1 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        l1 = ScreenSegment(a1, b1, plot.draw_color)
        l2 = ScreenSegment(b1, c1, plot.draw_color)
        l3 = ScreenSegment(c1, a1, plot.draw_color)
        select_screen_point(plot, create_plane_3p, 4,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'], 'y2': kwargs['y2'],
                             'x3': kwargs['x'], 'y3': kwargs['c']},
                            'xz', objects=(a1, b1, c1, l1, l2, l3), x=kwargs['x1'], c=kwargs['y1'])
    elif step == 5:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        c1 = ScreenPoint(kwargs['x3'], kwargs['y3'], plot.draw_color)
        l1 = ScreenSegment(a1, b1, plot.draw_color)
        l2 = ScreenSegment(b1, c1, plot.draw_color)
        l3 = ScreenSegment(c1, a1, plot.draw_color)
        a2 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(plot, create_plane_3p, 5,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'], 'y2': kwargs['y2'],
                             'x3': kwargs['x3'], 'y3': kwargs['y3'], 'z1': kwargs['c']},
                            'xz', objects=(a1, b1, c1, l1, l2, l3, a2, s1), x=kwargs['x2'], c=kwargs['y2'],
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 6:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        c1 = ScreenPoint(kwargs['x3'], kwargs['y3'], plot.draw_color)
        l1 = ScreenSegment(a1, b1, plot.draw_color)
        l2 = ScreenSegment(b1, c1, plot.draw_color)
        l3 = ScreenSegment(c1, a1, plot.draw_color)
        a2 = ScreenPoint(kwargs['x1'], kwargs['z1'], plot.draw_color)
        b2 = ScreenPoint(kwargs['x2'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        s2 = ScreenSegment(b1, b2, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        s3 = ScreenSegment(a2, b2, plot.draw_color)
        select_screen_point(plot, create_plane_3p, 6, kwargs, 'xz',
                            objects=(a1, b1, c1, l1, l2, l3, a2, b2, s1, s2, s3), x=kwargs['x3'], c=kwargs['y3'],
                            object_func=lambda pos: (ScreenSegment((kwargs['x2'], kwargs['c']), pos, plot.draw_color),
                                                     ScreenSegment((kwargs['x1'], kwargs['z1']), pos, plot.draw_color)),
                            final_func=lambda pos: plot.add_object(ag.Plane(ag.Point(
                                plot.plot_x_to_ag_x(kwargs['x1']),
                                plot.plot_y_to_ag_y(kwargs['y1']),
                                plot.plot_y_to_ag_z(kwargs['z1'])),
                                ag.Point(
                                    plot.plot_x_to_ag_x(kwargs['x2']),
                                    plot.plot_y_to_ag_y(kwargs['y2']),
                                    plot.plot_y_to_ag_z(kwargs['c'])),
                                ag.Point(
                                    plot.plot_x_to_ag_x(kwargs['x3']),
                                    plot.plot_y_to_ag_y(kwargs['y3']),
                                    plot.plot_y_to_ag_z(pos[1]))
                            ), end=True, draw_3p=True, draw_cl=True))


def create_parallel_plane(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_parallel_plane, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(plot, create_parallel_plane, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(
            plot, create_parallel_plane, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
            object_func=lambda pos: (GeneralObject(ag.Plane(kwargs['obj'].normal, ag.Point(
                plot.plot_x_to_ag_x(kwargs['x']),
                plot.plot_y_to_ag_y(kwargs['c']),
                plot.plot_y_to_ag_z(pos[1]))), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Plane(kwargs['obj'].normal, ag.Point(
                plot.plot_x_to_ag_x(kwargs['x']),
                plot.plot_y_to_ag_y(kwargs['c']),
                plot.plot_y_to_ag_z(pos[1]))), end=True))


def create_horizontal(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_horizontal, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(
            plot, create_horizontal, 2, kwargs, 'xy',
            object_func=lambda pos: (GeneralObject(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 0, 1)), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 0, 1)), end=True))


def create_frontal(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_frontal, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(
            plot, create_frontal, 2, kwargs, 'xy',
            object_func=lambda pos: (GeneralObject(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 1, 0)), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 1, 0)), end=True))


def get_distance(plot, step, **kwargs):
    if step == 1:
        plot.print('Select point, line or plane')
        select_object(plot, get_distance, 1, kwargs, (ag.Point, ag.Line, ag.Plane))
    elif step == 2:
        plot.print('Select point, line or plane')
        select_object(plot, get_distance, 2, {'obj1': kwargs['obj']}, (ag.Point, ag.Line, ag.Plane))
    elif step == 3:
        try:
            plot.print('Distance: {}'.format(
                ag.distance(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
        except Exception:
            try:
                plot.print('Distance: {}'.format(
                    ag.distance(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
            except Exception:
                plot.print('Error')


def get_angle(plot, step, **kwargs):
    if step == 1:
        plot.print('Select line or plane')
        select_object(plot, get_angle, 1, kwargs, (ag.Point, ag.Line, ag.Plane))
    elif step == 2:
        plot.print('Select line or plane')
        select_object(plot, get_angle, 2, {'obj1': kwargs['obj']}, (ag.Point, ag.Line, ag.Plane))
    elif step == 3:
        try:
            plot.print('Angle: {}'.format(
                ag.angle(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
        except Exception:
            try:
                plot.print('Angle: {}'.format(
                    ag.angle(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
            except Exception:
                plot.print('Error')


def create_circle(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_circle, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(plot, create_circle, 2, kwargs, 'xy', object_func=lambda pos: (
            GeneralObject(ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                   plot.plot_y_to_ag_y(pos[1]),
                                   kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                                            plot.plot_y_to_ag_y(pos[1]))),
                          color=plot.draw_color),))
    elif step == 3:
        center = ag.Point(plot.plot_x_to_ag_x(kwargs['x']),
                          plot.plot_y_to_ag_y(kwargs['c']),
                          kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(kwargs['x']),
                                                                   plot.plot_y_to_ag_y(kwargs['c'])))
        select_screen_point(
            plot, create_circle, 3, kwargs, 'xy',
            object_func=lambda pos: (GeneralObject(ag.Circle(center, ag.distance(center, ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1])))),
                                                             kwargs['obj'].general_object.ag_object.normal),
                                                   color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Circle(center, ag.distance(center, ag.Point(
                plot.plot_x_to_ag_x(pos[0]),
                plot.plot_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                         plot.plot_y_to_ag_y(pos[1])))),
                                                             kwargs['obj'].general_object.ag_object.normal),
                                                   end=True))


def create_cone(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_cone, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_cone, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(plot, create_cone, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        s2 = ScreenSegment(a1, b1, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(
            plot, create_cone, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                   'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 5:
        p1 = ag.Point(plot.plot_x_to_ag_x(kwargs['x1']), plot.plot_y_to_ag_y(kwargs['y1']),
                      plot.plot_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.plot_x_to_ag_x(kwargs['x2']), plot.plot_y_to_ag_y(kwargs['y2']),
                      plot.plot_y_to_ag_z(kwargs['c']))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        select_screen_point(
            plot, create_cone, 5, dict(), 'xy',
            object_func=lambda pos: (GeneralObject(ag.Cone(p1, p2, ag.distance(p1, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                plane.z(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]))
            ))), color=plot.draw_color),),
            final_func=lambda pos: plot.add_object(ag.Cone(p1, p2, ag.distance(p1, ag.Point(
                plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                plane.z(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]))
            ))), end=True))


def create_sphere(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_sphere, 1, kwargs, 'xy')
    elif step == 2:
        a = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_sphere, 2, {'x0': kwargs['x'], 'y': kwargs['c']}, 'xz', x=kwargs['x'],
                            c=kwargs['c'], objects=(a,))
    elif step == 3:
        center = GeneralObject(ag.Point(
            plot.plot_x_to_ag_x(kwargs['x']),
            plot.plot_y_to_ag_y(kwargs['y']),
            plot.plot_y_to_ag_z(kwargs['c'])
        ), color=plot.draw_color)
        select_screen_point(plot, create_sphere, 3, kwargs, 'xy', objects=(center,),
                            object_func=lambda pos: (
                                GeneralObject(ag.Sphere(center.ag_object, ag.distance(center.ag_object, ag.Point(
                                    plot.plot_x_to_ag_x(pos[0]),
                                    plot.plot_y_to_ag_y(pos[1]),
                                    center.ag_object.z))),
                                              color=plot.draw_color),),
                            final_func=lambda pos: plot.add_object(
                                ag.Sphere(center.ag_object, ag.distance(center.ag_object, ag.Point(
                                    plot.plot_x_to_ag_x(pos[0]),
                                    plot.plot_y_to_ag_y(pos[1]),
                                    center.ag_object.z))),
                                end=True))


def get_intersection(plot, step, **kwargs):
    if step == 1:
        plot.print('Select first object')
        select_object(plot, get_intersection, 1, kwargs)
    elif step == 2:
        plot.print('Select second object')
        select_object(plot, get_intersection, 2, {'obj1': kwargs['obj']})
    elif step == 3:
        try:
            res = kwargs['obj1'].general_object.ag_object.intersection(kwargs['obj'].general_object.ag_object)
        except Exception as ex:
            raise ex
            try:
                res = kwargs['obj'].general_object.ag_object.intersection(kwargs['obj1'].general_object.ag_object)
            except Exception:
                plot.print('Error')
                return
        if res is not None:
            if isinstance(res, tuple):
                plot.add_object(ag.IntersectionObject(kwargs['obj'].general_object.ag_object,
                                                      kwargs['obj1'].general_object.ag_object, res))
                plot.end()
            else:
                plot.add_object(res, end=True)
            plot.print('Complete')
        else:
            plot.print('No intersection')


def create_spline(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_spline, 1, {'points': []}, (ag.Plane,))
    elif step == 2:
        def mouse_move(pos):
            pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
            point = ag.Point(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                             kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                                      plot.plot_y_to_ag_y(pos[1])))
            spline = point
            if len(kwargs['points']) == 1:
                spline = ag.Segment(kwargs['points'][0], point)
            elif len(kwargs['points']) > 1:
                spline = ag.Spline(kwargs['obj'].general_object.ag_object, *kwargs['points'], point)
            plot.update(GeneralObject(point, color=plot.draw_color), GeneralObject(spline, color=plot.draw_color))

        def mouse_left(pos):
            pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
            point = ag.Point(plot.plot_x_to_ag_x(pos[0]), plot.plot_y_to_ag_y(pos[1]),
                             kwargs['obj'].general_object.ag_object.z(plot.plot_x_to_ag_x(pos[0]),
                                                                      plot.plot_y_to_ag_y(pos[1])))
            create_spline(plot, 2, obj=kwargs['obj'], points=kwargs['points'] + [point])

        def enter_pressed(pos):
            plot.add_object(ag.Spline(kwargs['obj'].general_object.ag_object, kwargs['points']), end=True)

        plot.mouse_move = mouse_move
        plot.mouse_left = mouse_left
        plot.enter = enter_pressed
        plot.mouse_right = lambda *args: create_spline(plot, 2, obj=kwargs['obj'], points=kwargs['points'][:-1])


def create_rotation_surface(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_rotation_surface, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(kwargs['x'], kwargs['c'], color=plot.draw_color)
        select_screen_point(plot, create_rotation_surface, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy',
                            objects=(a1,),
                            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 3:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        select_screen_point(plot, create_rotation_surface, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(kwargs['x1'], kwargs['y1'], plot.draw_color)
        a2 = ScreenPoint(kwargs['x2'], kwargs['y2'], plot.draw_color)
        b1 = ScreenPoint(kwargs['x1'], kwargs['c'], plot.draw_color)
        s1 = ScreenSegment(a1, a2, plot.draw_color)
        s2 = ScreenSegment(a1, b1, plot.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)
        select_screen_point(
            plot, create_rotation_surface, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                               'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment((kwargs['x'], kwargs['c']), pos, plot.draw_color),))
    elif step == 5:
        p1 = ag.Point(plot.plot_x_to_ag_x(kwargs['x1']), plot.plot_y_to_ag_y(kwargs['y1']),
                      plot.plot_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.plot_x_to_ag_x(kwargs['x2']), plot.plot_y_to_ag_y(kwargs['y2']),
                      plot.plot_y_to_ag_z(kwargs['c']))
        if ag.Vector(p1, p2) | ag.Vector(0, 0, 1):
            plane = ag.Plane(p1, p2, ag.Vector(0, 1, 0) & ag.Vector(p1, p2))
            l1 = projections.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xz', plot.cl_color)
            l2 = projections.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xz', plot.cl_color)

            def mouse_move(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plane.y(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_z(pos[1])),
                                 plot.plot_y_to_ag_z(pos[1]))
                plot.update(GeneralObject(point, color=plot.draw_color),
                            GeneralObject(ag.Segment(p1, p2), color=plot.draw_color), l1, l2)

            def mouse_left(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plane.y(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_z(pos[1])),
                                 plot.plot_y_to_ag_z(pos[1]))
                create_rotation_surface(plot, 6, **kwargs, points=[point])

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
        else:
            plane = ag.Plane(p1, p2, ag.Vector(0, 0, 1) & ag.Vector(p1, p2))
            l1 = projections.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xy', plot.cl_color)
            l2 = projections.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xy', plot.cl_color)

            def mouse_move(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plot.plot_y_to_ag_y(pos[1]),
                                 plane.z(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_y(pos[1])))
                plot.update(GeneralObject(point, color=plot.draw_color),
                            GeneralObject(ag.Segment(p1, p2), color=plot.draw_color), l1, l2)

            def mouse_left(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plot.plot_y_to_ag_y(pos[1]),
                                 plane.z(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_y(pos[1])))
                create_rotation_surface(plot, 6, **kwargs, points=[point])

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
    elif step == 6:
        p1 = ag.Point(plot.plot_x_to_ag_x(kwargs['x1']), plot.plot_y_to_ag_y(kwargs['y1']),
                      plot.plot_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.plot_x_to_ag_x(kwargs['x2']), plot.plot_y_to_ag_y(kwargs['y2']),
                      plot.plot_y_to_ag_z(kwargs['c']))
        v = ag.Vector(p1, p2) * (1 / ag.distance(p1, p2))
        if ag.Vector(p1, p2) | ag.Vector(0, 0, 1):
            plane = ag.Plane(p1, p2, ag.Vector(0, 1, 0) & ag.Vector(p1, p2))
            l1 = projections.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xz', plot.cl_color)
            l2 = projections.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xz', plot.cl_color)

            def mouse_move(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xz')
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plane.y(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_z(pos[1])),
                                 plot.plot_y_to_ag_z(pos[1]))

                if len(kwargs['points']) == 1:
                    spline = ag.Segment(kwargs['points'][0], point)
                else:
                    spline = ag.Spline(plane, *kwargs['points'], point)
                plot.update(GeneralObject(point, color=plot.draw_color),
                            GeneralObject(ag.Segment(p1, p2), color=plot.draw_color),
                            GeneralObject(spline, color=plot.draw_color), l1, l2)

            def mouse_left(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xz')
                if distance(pos, nearest_point(pos, l2, as_line=True)) < 10:
                    pos = nearest_point(pos, l2, as_line=True)
                    point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                     plane.y(plot.plot_x_to_ag_x(pos[0]),
                                             plot.plot_y_to_ag_z(pos[1])),
                                     plot.plot_y_to_ag_z(pos[1]))
                    kwargs['points'].append(point)
                    kwargs['points'][0] += -v
                    kwargs['points'][-1] += v
                    plot.add_object(ag.RotationSurface(p1, p2, ag.Spline(plane, kwargs['points'])), end=True)
                else:
                    point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                     plane.y(plot.plot_x_to_ag_x(pos[0]),
                                             plot.plot_y_to_ag_z(pos[1])),
                                     plot.plot_y_to_ag_z(pos[1]))
                    kwargs['points'].append(point)
                    create_rotation_surface(plot, 6, **kwargs)

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
        else:
            plane = ag.Plane(p1, p2, ag.Vector(0, 0, 1) & ag.Vector(p1, p2))
            l1 = projections.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xy', plot.cl_color)
            l2 = projections.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xy', plot.cl_color)

            def mouse_move(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
                point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                 plot.plot_y_to_ag_y(pos[1]),
                                 plane.z(plot.plot_x_to_ag_x(pos[0]),
                                         plot.plot_y_to_ag_y(pos[1])))

                if len(kwargs['points']) == 1:
                    spline = ag.Segment(kwargs['points'][0], point)
                else:
                    spline = ag.Spline(plane, *kwargs['points'], point)
                plot.update(GeneralObject(point, color=plot.draw_color),
                            GeneralObject(ag.Segment(p1, p2), color=plot.draw_color),
                            GeneralObject(spline, color=plot.draw_color), l1, l2)

            def mouse_left(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
                if distance(pos, nearest_point(pos, l2, as_line=True)) < 10:
                    pos = nearest_point(pos, l2, as_line=True)
                    point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                     plot.plot_y_to_ag_y(pos[1]),
                                     plane.z(plot.plot_x_to_ag_x(pos[0]),
                                             plot.plot_y_to_ag_y(pos[1])))
                    kwargs['points'].append(point)
                    kwargs['points'][0] += -v
                    kwargs['points'][-1] += v
                    plot.add_object(ag.RotationSurface(p1, p2, ag.Spline(plane, kwargs['points'])), end=True)
                else:
                    point = ag.Point(plot.plot_x_to_ag_x(pos[0]),
                                     plot.plot_y_to_ag_y(pos[1]),
                                     plane.z(plot.plot_x_to_ag_x(pos[0]),
                                             plot.plot_y_to_ag_y(pos[1])))
                    kwargs['points'].append(point)
                    create_rotation_surface(plot, 6, **kwargs)

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left


class _AGObject:
    def __init__(self, ag_class, *args, color=None):
        self.ag_class = ag_class
        self.args = args
        self._color = color

    def __call__(self, pos, *, _return_ag=False):
        lst = []
        for arg in self.args:
            if isinstance(arg, _AGObject):
                lst.append(arg(pos, _return_ag=True))
            elif callable(arg):
                lst.append(arg(pos))
            else:
                lst.append(arg)
        if _return_ag:
            return self.ag_class(*lst)
        return self.ag_class(*lst)

    def __add__(self, other: '_AGObject'):
        return _AgAriphmeticObject(self, other, self.ag_class.__add__)

    def __mul__(self, other: '_AGObject'):
        return _AgAriphmeticObject(self, other, self.ag_class.__mul__)

    def __truediv__(self, other: '_AGObject'):
        return _AgAriphmeticObject(self, other, self.ag_class.__truediv__)

    def __sub__(self, other: '_AGObject'):
        return _AgAriphmeticObject(self, other, self.ag_class.__sub__)


class _AgAriphmeticObject:
    def __init__(self, obj1, obj2, func):
        self.obj1 = obj1
        self.obj2 = obj2
        self.func = func

    def __call__(self, pos):
        return self.func(self.obj1(pos), self.obj2(pos))


class Drawer(QThread):
    POINT = 0
    SEGMENT = 1
    CYLINDER = 2
    SPHERE = 3
    INTERSECTION = 4
    TOR = 5
    CONE = 6
    LINE = 7
    PLANE = 8
    PLANE_3P = 9
    PERPENDICULAR_LINE = 10

    def __init__(self, canvass, obj, inversion=False):
        super().__init__()
        self.canvass = canvass
        self.obj = obj
        self.sm = SnapManager(self.canvass.object_manager)
        self.inversion = inversion
        self.first_plane = 'xz' if inversion else 'xy'
        self.second_plane = 'xy' if inversion else 'xz'

        self._on_mouse_move = None
        self._on_mouse_left = None
        self._on_mouse_right = None
        self._on_enter = None
        self._on_esc = None

        self._res_pos = None
        self._res_obj = None
        self.result = None

        self._temp_objects = []

    def _set_res_pos(self, pos):
        self._res_pos = pos

    def _set_res_obj(self, obj):
        self._res_obj = obj

    def mouse_move(self, pos: QPoint):
        if self._on_mouse_move:
            self._on_mouse_move(pos)

    def mouse_left(self, pos: QPoint):
        if self._on_mouse_left:
            self._on_mouse_left(pos)

    def mouse_right(self, pos: QPoint):
        if self._on_mouse_right:
            self._on_mouse_right(pos)

    def enter(self):
        if self._on_enter:
            self._on_enter()

    def esc(self):
        if self._on_esc:
            self._on_esc()

    def _screen_point(self, x=None, y=None):
        return lambda pos: ScreenPoint(x if x is not None else pos.x(), y if y is not None else pos.y(),
                                       self.canvass.draw_color)

    def _connection_line(self, x1, y1, x2=None, y2=None):
        return lambda pos: ScreenSegment((x1, y1),
                                         (x2 if x2 is not None else pos.x(), y2 if y2 is not None else pos.y()),
                                         self.canvass.cl_color, thickness=1, line_type=Qt.PenStyle.DashLine)

    def _screen_segment(self, x1, y1, x2=None, y2=None):
        return lambda pos: ScreenSegment((x1, y1),
                                         (x2 if x2 is not None else pos.x(), y2 if y2 is not None else pos.y()),
                                         self.canvass.draw_color)

    def _ag_point(self, x=None, y=None, z=None):
        def func(pos=None):
            x2, y2, z2 = x, y, z
            if x2 is None:
                x2 = pos.x()
            if y2 is None:
                y2 = pos.y()
            if z2 is None:
                z2 = pos.y()
            if self.inversion:
                y2, z2 = z2, y2
            x2 = projections.screen_x_to_ag_x(x2)
            y2 = projections.screen_y_to_ag_y(y2)
            z2 = projections.screen_y_to_ag_z(z2)
            return ag.Point(x2, y2, z2)

        return func

    def _ag_object(self, ag_class, *args):
        return _AGObject(ag_class, *args, color=self.canvass.draw_color)

    def _update(self, objects):
        self.canvass.set_temp_objects(*self._temp_objects, *objects)

    def _set_hover(self, obj):
        if obj is None:
            self.canvass.set_hover_objects()
        else:
            self.canvass.set_hover_objects(obj)

    def _select_screen_point(self, *objects, plane='xy', x=None, c=None):
        self._res_pos = None

        def mouse_move(pos):
            pos = self.sm.get_snap(pos, plane, x, c)
            self._update([obj(pos) for obj in objects])

        def mouse_left(pos):
            pos = self.sm.get_snap(pos, plane, x, c)
            self._set_res_pos(pos)

        self._on_mouse_move = mouse_move
        self._on_mouse_left = mouse_left
        self._on_mouse_right = lambda pos: self.terminate()

        while True:
            if self._res_pos is not None:
                for obj in objects:
                    self._temp_objects.append(obj(self._res_pos))
                return self._res_pos.x(), self._res_pos.y()
            sleep(0.1)

    def _select_general_object(self, *objects, types=None):
        self._res_obj = None

        def mouse_move(pos):
            obj = self.canvass.object_by_pos((pos.x(), pos.y()))
            if obj is None or types is None or obj.ag_object.__class__ in types:
                self._set_hover(obj)

        def mouse_left(pos):
            obj = self.canvass.object_by_pos((pos.x(), pos.y()))
            if obj is None or types is None or obj.ag_object.__class__ in types:
                self._set_res_obj(obj)

        self._on_mouse_move = mouse_move
        self._on_mouse_left = mouse_left
        self._on_mouse_right = lambda pos: self.terminate()

        while True:
            if self._res_obj is not None:
                for obj in objects:
                    self._temp_objects.append(obj(self._res_pos))
                self._on_mouse_move = None
                self._on_mouse_right = None
                self._on_mouse_left = None
                return self._res_obj
            sleep(0.1)

    def run(self):
        match self.obj:
            case Drawer.POINT:
                self.draw_point()
            case Drawer.SEGMENT:
                self.draw_segment()
            case Drawer.CYLINDER:
                self.draw_cylinder()
            case Drawer.SPHERE:
                self.draw_sphere()
            case Drawer.INTERSECTION:
                self.draw_intersection()
            case Drawer.TOR:
                self.draw_tor()
            case Drawer.CONE:
                self.draw_cone()
            case Drawer.LINE:
                self.draw_line()
            case Drawer.PLANE:
                self.draw_plane()
            case Drawer.PLANE_3P:
                self.draw_plane_3p()
            case Drawer.PERPENDICULAR_LINE:
                self.draw_perpendicular()

    def draw_point(self):
        x, y = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        _, z = self._select_screen_point(self._screen_point(x=x), self._connection_line(x, y, x2=x), plane=self.second_plane, x=x)
        self.result = self._ag_point(x, y, z)()

    def draw_segment(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        _, z2 = self._select_screen_point(self._screen_point(x=x2), self._connection_line(x2, y2, x2=x2),
                                          self._screen_segment(x1, z1, x2=x2), plane=self.second_plane)
        self.result = ag.Segment(self._ag_point(x1, y1, z1)(), self._ag_point(x2, y2, z2)())

    def draw_line(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        p1 = self._ag_point(x1, y1, z1)()
        _, z2 = self._select_screen_point(self._screen_point(x=x2), self._connection_line(x2, y2, x2=x2),
                                          self._ag_object(ag.Line, p1, self._ag_point(x=x2, y=y2)), plane=self.second_plane)
        self.result = ag.Line(self._ag_point(x1, y1, z1)(), self._ag_point(x2, y2, z2)())

    def draw_perpendicular(self):
        obj = self._select_general_object(types=[ag.Line, ag.Plane]).ag_object
        x, y = self._select_screen_point(self._screen_point())
        _, z = self._select_screen_point(self._screen_point(x=x), self._connection_line(x, y, x2=x))
        point = self._ag_point(x, y, z)()
        if isinstance(obj, ag.Plane):
            vector = obj.normal
        elif isinstance(obj, ag.Line):
            vector = ag.Plane(obj.point, obj.vector, point).normal & obj.vector
        else:
            raise TypeError
        self.result = ag.Line(point, vector)

    def draw_plane(self):
        x, _ = self._select_screen_point(self._screen_point(y=CANVASS_Y // 2), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x, CANVASS_Y // 2), plane=self.first_plane)
        x3, z3 = self._select_screen_point(self._screen_point(), self._screen_segment(x, CANVASS_Y // 2), plane=self.second_plane)
        self.result = ag.Plane(self._ag_point(x, CANVASS_Y // 2, CANVASS_Y // 2)(),
                               self._ag_point(x2, y2, CANVASS_Y // 2)(),
                               self._ag_point(x3, CANVASS_Y // 2, z3)())

    def draw_plane_3p(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1), plane=self.first_plane)
        x3, y3 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1),
                                           self._screen_segment(x2, y2), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        _, z2 = self._select_screen_point(self._screen_point(x=x2), self._connection_line(x2, y2, x2=x2),
                                          self._screen_segment(x1, z1, x2=x2), plane=self.second_plane)
        _, z3 = self._select_screen_point(self._screen_point(x=x3), self._connection_line(x3, y3, x2=x3),
                                          self._screen_segment(x1, z1, x2=x3), self._screen_segment(x2, z2, x2=x3),
                                          plane=self.second_plane)
        self.result = ag.Plane(self._ag_point(x1, y1, z1)(), self._ag_point(x2, y2, z2)(),
                               self._ag_point(x3, y3, z3)())

    def draw_cylinder(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        _, z2 = self._select_screen_point(self._screen_point(x=x2), self._connection_line(x2, y2, x2=x2),
                                          self._screen_segment(x1, z1, x2=x2), plane=self.second_plane)
        p1 = self._ag_point(x1, y1, z1)()
        p2 = self._ag_point(x2, y2, z2)()
        plane = ag.Plane(ag.Vector(p1, p2), p1)

        xr, yr = self._select_screen_point(
            self._ag_object(ag.Cylinder, p1, p2, lambda pos: ag.distance(p1, ag.Point(
                projections.screen_x_to_ag_x(pos.x()),
                projections.screen_y_to_ag_y(pos.y()),
                plane.z(projections.screen_x_to_ag_x(pos.x()),
                        projections.screen_y_to_ag_y(pos.y()))))))

        self.result = ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
            projections.screen_x_to_ag_x(xr),
            projections.screen_y_to_ag_y(yr),
            plane.z(projections.screen_x_to_ag_x(xr),
                    projections.screen_y_to_ag_y(yr)))))

    def draw_cone(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        x2, y2 = self._select_screen_point(self._screen_point(), self._screen_segment(x1, y1), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        _, z2 = self._select_screen_point(self._screen_point(x=x2), self._connection_line(x2, y2, x2=x2),
                                          self._screen_segment(x1, z1, x2=x2), plane=self.second_plane)
        p1 = self._ag_point(x1, y1, z1)()
        p2 = self._ag_point(x2, y2, z2)()
        plane = ag.Plane(ag.Vector(p1, p2), p1)

        xr, yr = self._select_screen_point(
            self._ag_object(ag.Cone, p1, p2, lambda pos: ag.distance(p1, ag.Point(
                projections.screen_x_to_ag_x(pos.x()),
                projections.screen_y_to_ag_y(pos.y()),
                plane.z(projections.screen_x_to_ag_x(pos.x()),
                        projections.screen_y_to_ag_y(pos.y()))))))

        self.result = ag.Cone(p1, p2, ag.distance(p1, ag.Point(
            projections.screen_x_to_ag_x(xr),
            projections.screen_y_to_ag_y(yr),
            plane.z(projections.screen_x_to_ag_x(xr),
                    projections.screen_y_to_ag_y(yr)))))

    def draw_tor(self):
        x1, y1 = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        _, z1 = self._select_screen_point(self._screen_point(x=x1), self._connection_line(x1, y1, x2=x1), plane=self.second_plane)
        center = self._ag_point(x1, y1, z1)()

        xd, yd = self._select_screen_point(lambda pos: ag.Circle(center, ag.distance(
            center, self._ag_point(pos.x(), pos.y(), z1)())), plane=self.first_plane)
        radius = ag.distance(center, self._ag_point(xd, yd, z1)())
        self._temp_objects.pop()

        x2, y2 = self._select_screen_point(
            self._ag_object(ag.Circle, center, radius, self._ag_object(ag.Vector, center, self._ag_point(z=z1))), plane=self.first_plane)
        self._temp_objects.pop()
        _, z2 = self._select_screen_point(
            self._ag_object(ag.Circle, center, radius, self._ag_object(ag.Vector, center, self._ag_point(x2, y2))), plane=self.second_plane)
        vector = ag.Vector(center, self._ag_point(x2, y2, z2)())
        self._temp_objects.pop()

        xr, yr = self._select_screen_point(self._ag_object(ag.Tor, center, radius, lambda pos: ag.distance(
            center, self._ag_point(z=z1)(pos)), vector))

        self.result = ag.Tor(center, radius, ag.distance(
            center, self._ag_point(xr, yr, z1)()), vector)

    def draw_sphere(self):
        x, y = self._select_screen_point(self._screen_point(), plane=self.first_plane)
        _, z = self._select_screen_point(self._screen_point(x=x), self._connection_line(x, y, x2=x), plane=self.second_plane)
        p = self._ag_point(x, y, z)()
        xd, yd = self._select_screen_point(self._ag_object(ag.Sphere, p, lambda pos: ag.distance(
            p, self._ag_point(z=z)(pos))), plane=self.first_plane)

        self.result = ag.Sphere(p, ag.distance(p, self._ag_point(xd, yd, z)()))

    def draw_intersection(self):
        obj1 = self._select_general_object().ag_object
        print(1, obj1)
        obj2 = self._select_general_object().ag_object
        print(2, obj2)

        self.result = obj1.intersection(obj2)
        print(3, self.result)
