from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
from utils.drawing.projections.projection_manager import ScreenCircle
from utils.drawing.projections.plot_object import TempObject
from utils.drawing.snap import distance, nearest_point
import core.angem as ag
from PyQt5.QtCore import Qt

COLOR1 = (0, 162, 232)
COLOR_CONNECT_LINE = (180, 180, 180)
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
                    plot.update(ScreenSegment(plot, (x, c), pos, color=COLOR_CONNECT_LINE, thickness=1,
                                              line_type=Qt.DashLine), *object_func(pos), *objects,
                                ScreenPoint(plot, *pos, color=COLOR1))
                else:
                    plot.update(ScreenSegment(plot, (x, c), pos, color=COLOR_CONNECT_LINE, thickness=1,
                                              line_type=Qt.DashLine), *object_func(pos), *objects)
            else:
                plot.update(ScreenSegment(plot, (x, c), pos, color=COLOR_CONNECT_LINE, thickness=1,
                                          line_type=Qt.DashLine), *objects,
                            ScreenPoint(plot, *pos, color=COLOR1))

        elif object_func:
            if draw_point:
                plot.update(*objects, ScreenPoint(plot, *pos, color=COLOR1), *object_func(pos))
            else:
                plot.update(*objects, *object_func(pos))
        else:
            plot.update(*objects, ScreenPoint(plot, *pos, color=COLOR1))

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

    plot.cmd_command = command
    plot.setCmdStatus.emit(True)


def convert_point(plot, x, y, z):
    if not isinstance(y, int) and not isinstance(y, float):
        x = plot.pm.convert_screen_x_to_ag_x(x)
        z = plot.pm.convert_screen_y_to_ag_z(z)
        return x, y(x, z), z
    if not isinstance(z, int) and not isinstance(z, float):
        x = plot.pm.convert_screen_x_to_ag_x(x)
        y = plot.pm.convert_screen_y_to_ag_y(y)
        return x, y, z(x, y)
    return plot.pm.convert_screen_x_to_ag_x(x), plot.pm.convert_screen_y_to_ag_y(y), plot.pm.convert_screen_y_to_ag_z(z)


def create_point(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_point, 1, kwargs, 'xy')
        cmd_command(plot, 3, lambda x, y, z: plot.add_object(ag.Point(x, y, z), end=True))
    elif step == 2:
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_point, 2, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                            final_func=lambda pos: plot.add_object(ag.Point(
                                *convert_point(plot, kwargs['x'], kwargs['c'], pos[1])), end=True))


def create_segment(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_segment, 1, kwargs, 'xy')
        cmd_command(plot, 3, lambda x, y, z: create_segment(
            plot, 3, x1=plot.pm.ag_x_to_screen_x(x), y1=plot.pm.ag_y_to_screen_y(y), c=plot.pm.ag_y_to_screen_z(z)))
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_segment, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(plot, create_segment, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
        cmd_command(plot, 3, lambda x, y, z: plot.add_object(ag.Segment(ag.Point(
            *convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])), ag.Point(x, y, z)), end=True))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        s2 = ScreenSegment(plot, a1, b1, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(
            plot, create_segment, 3, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                      'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Segment(
                ag.Point(*convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])),
                ag.Point(*convert_point(plot, kwargs['x2'], kwargs['y2'], pos[1]))
            ), end=True, draw_cl=True))


def create_line(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_line, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_line, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(plot, create_line, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        s2 = ScreenSegment(plot, a1, b1, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(
            plot, create_line, 3, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                   'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Line(
                ag.Point(*convert_point(plot, kwargs['x1'], kwargs['y1'], kwargs['c'])),
                ag.Point(*convert_point(plot, kwargs['x2'], kwargs['y2'], pos[1]))
            ), end=True))


def create_plane(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_plane, 1, kwargs, 'xy', c=plot.axis.lp[1])
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], plot.axis.lp[1], color=COLOR1)
        select_screen_point(plot, create_plane, 2, {'x0': kwargs['x']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], plot.axis.lp[1]), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x0'], plot.axis.lp[1], color=COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(
            plot, create_plane, 3, {'x0': kwargs['x0'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xz', objects=(a1, a2, s1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x0'], plot.axis.lp[1]), pos, COLOR1),),
            final_func=lambda pos: plot.add_object(
                ag.Plane(ag.Vector(ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x0']), 0, 0),
                                   ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                                            plot.pm.convert_screen_y_to_ag_y(kwargs['c']))) & ag.Vector(
                    ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x0']), 0, 0),
                    ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]), 0, plot.pm.convert_screen_y_to_ag_z(pos[1])
                             )),
                         ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x0']), 0, 0)), end=True))


def create_cylinder(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_cylinder, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_cylinder, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(plot, create_cylinder, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        s2 = ScreenSegment(plot, a1, b1, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(
            plot, create_cylinder, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                       'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 5:
        p1 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        select_screen_point(
            plot, create_cylinder, 5, dict(), 'xy',
            object_func=lambda pos: (TempObject(plot, ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), end=True))


def create_perpendicular_segment(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment, line or plane')
        select_object(plot, create_perpendicular_segment, 1, kwargs, (ag.Line, ag.Plane, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_perpendicular_segment, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        if isinstance(kwargs['obj'], ag.Segment):
            kwargs['obj'] = ag.Line(kwargs['obj'].p1, kwargs['obj'].p2)
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        if isinstance(kwargs['obj'], ag.Line):
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Segment(ag.Point(
                    plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                    plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                    plot.pm.convert_screen_y_to_ag_z(pos[1])),
                    ag.Line(ag.Point(
                        plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                        plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                        plot.pm.convert_screen_y_to_ag_z(pos[1])),
                        kwargs['obj'].vector & ag.Plane(kwargs['obj'], ag.Point(
                            plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                            plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                            plot.pm.convert_screen_y_to_ag_z(pos[1]))).normal).intersection(kwargs['obj'])
                ), end=True))
        else:
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Segment(ag.Point(
                    plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                    plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                    plot.pm.convert_screen_y_to_ag_z(pos[1])),
                    ag.Line(ag.Point(
                        plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                        plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                        plot.pm.convert_screen_y_to_ag_z(pos[1])),
                        kwargs['obj'].normal).intersection(kwargs['obj'])
                ), end=True, draw_cl=True))


def create_parallel_segment(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment or line')
        select_object(plot, create_parallel_segment, 1, kwargs, (ag.Line, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_parallel_segment, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(
            plot, create_parallel_segment, 3, {'obj': kwargs['obj'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xy', x=kwargs['x'], c=kwargs['c'], objects=(a1,))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], color=COLOR1)
        a2 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], color=COLOR1)
        s1 = ScreenSegment(plot, a1, a2, color=COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        if isinstance(kwargs['obj'], ag.Segment):
            v = ag.Vector(kwargs['obj'].p1, kwargs['obj'].p2)
        else:
            v = kwargs['obj'].vector
        point = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                         plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        line = ag.Line(point, v)
        select_screen_point(
            plot, create_parallel_segment, 4, {'obj': kwargs['obj'], 'x1': kwargs['x'], 'y1': kwargs['c']},
            'xy', objects=(a1, a2, s1),
            object_func=lambda pos: (TempObject(plot, ag.Segment(point, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), line.y(x=plot.pm.convert_screen_x_to_ag_x(pos[0])),
                line.z(x=plot.pm.convert_screen_x_to_ag_x(pos[0])))), color=COLOR1),), draw_point=False,
            final_func=lambda pos: plot.add_object(ag.Segment(point, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), line.y(x=plot.pm.convert_screen_x_to_ag_x(pos[0])),
                line.z(x=plot.pm.convert_screen_x_to_ag_x(pos[0])))), end=True, draw_cl=True))


def create_perpendicular_line(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment, line or plane')
        select_object(plot, create_perpendicular_line, 1, kwargs, (ag.Line, ag.Plane, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_perpendicular_line, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        if isinstance(kwargs['obj'], ag.Segment):
            kwargs['obj'] = ag.Line(kwargs['obj'].p1, kwargs['obj'].p2)
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        if isinstance(kwargs['obj'], ag.Line):
            select_screen_point(
                plot, create_perpendicular_line, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                    plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                    plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                    plot.pm.convert_screen_y_to_ag_z(pos[1])),
                    kwargs['obj'].vector & ag.Plane(kwargs['obj'], ag.Point(
                        plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                        plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                        plot.pm.convert_screen_y_to_ag_z(pos[1]))).normal), end=True))
        else:
            select_screen_point(
                plot, create_perpendicular_segment, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                    plot.pm.convert_screen_x_to_ag_x(kwargs['x']), plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                    plot.pm.convert_screen_y_to_ag_z(pos[1])), kwargs['obj'].normal), end=True))


def create_parallel_line(plot, step, **kwargs):
    if step == 1:
        plot.print('Select segment or line')
        select_object(plot, create_parallel_line, 1, kwargs, (ag.Line, ag.Segment))
    elif step == 2:
        select_screen_point(plot, create_parallel_line, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        if isinstance(kwargs['obj'], ag.Segment):
            v = ag.Vector(kwargs['obj'].p1, kwargs['obj'].p2)
        else:
            v = kwargs['obj'].vector
        select_screen_point(
            plot, create_parallel_line, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
            object_func=lambda pos: (TempObject(plot, ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                plot.pm.convert_screen_y_to_ag_z(pos[1])), v), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                plot.pm.convert_screen_y_to_ag_z(pos[1])), v), end=True))


def create_plane_3p(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_plane_3p, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_plane_3p, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        l1 = ScreenSegment(plot, a1, b1, COLOR1)
        select_screen_point(plot, create_plane_3p, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xy', objects=(a1, b1, l1),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x1'], kwargs['y1']), pos, COLOR1),
                                                     ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1)))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        c1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        l1 = ScreenSegment(plot, a1, b1, COLOR1)
        l2 = ScreenSegment(plot, b1, c1, COLOR1)
        l3 = ScreenSegment(plot, c1, a1, COLOR1)
        select_screen_point(plot, create_plane_3p, 4,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'], 'y2': kwargs['y2'],
                             'x3': kwargs['x'], 'y3': kwargs['c']},
                            'xz', objects=(a1, b1, c1, l1, l2, l3), x=kwargs['x1'], c=kwargs['y1'])
    elif step == 5:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        c1 = ScreenPoint(plot, kwargs['x3'], kwargs['y3'], COLOR1)
        l1 = ScreenSegment(plot, a1, b1, COLOR1)
        l2 = ScreenSegment(plot, b1, c1, COLOR1)
        l3 = ScreenSegment(plot, c1, a1, COLOR1)
        a2 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(plot, create_plane_3p, 5,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'], 'y2': kwargs['y2'],
                             'x3': kwargs['x3'], 'y3': kwargs['y3'], 'z1': kwargs['c']},
                            'xz', objects=(a1, b1, c1, l1, l2, l3, a2, s1), x=kwargs['x2'], c=kwargs['y2'],
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 6:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        c1 = ScreenPoint(plot, kwargs['x3'], kwargs['y3'], COLOR1)
        l1 = ScreenSegment(plot, a1, b1, COLOR1)
        l2 = ScreenSegment(plot, b1, c1, COLOR1)
        l3 = ScreenSegment(plot, c1, a1, COLOR1)
        a2 = ScreenPoint(plot, kwargs['x1'], kwargs['z1'], COLOR1)
        b2 = ScreenPoint(plot, kwargs['x2'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        s2 = ScreenSegment(plot, b1, b2, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        s3 = ScreenSegment(plot, a2, b2, COLOR1)
        select_screen_point(plot, create_plane_3p, 6, kwargs, 'xz',
                            objects=(a1, b1, c1, l1, l2, l3, a2, b2, s1, s2, s3), x=kwargs['x3'], c=kwargs['y3'],
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x2'], kwargs['c']), pos, COLOR1),
                                                     ScreenSegment(plot, (kwargs['x1'], kwargs['z1']), pos, COLOR1)),
                            final_func=lambda pos: plot.add_object(ag.Plane(ag.Point(
                                plot.pm.convert_screen_x_to_ag_x(kwargs['x1']),
                                plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                                plot.pm.convert_screen_y_to_ag_z(kwargs['z1'])),
                                ag.Point(
                                    plot.pm.convert_screen_x_to_ag_x(kwargs['x2']),
                                    plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                                    plot.pm.convert_screen_y_to_ag_z(kwargs['c'])),
                                ag.Point(
                                    plot.pm.convert_screen_x_to_ag_x(kwargs['x3']),
                                    plot.pm.convert_screen_y_to_ag_y(kwargs['y3']),
                                    plot.pm.convert_screen_y_to_ag_z(pos[1]))
                            ), end=True, draw_3p=True, draw_cl=True))


def create_parallel_plane(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_parallel_plane, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(plot, create_parallel_plane, 2, {'obj': kwargs['obj'].general_object.ag_object}, 'xy')
    elif step == 3:
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(
            plot, create_parallel_plane, 3, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
            object_func=lambda pos: (TempObject(plot, ag.Plane(kwargs['obj'].normal, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                plot.pm.convert_screen_y_to_ag_z(pos[1]))), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Plane(kwargs['obj'].normal, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                plot.pm.convert_screen_y_to_ag_z(pos[1]))), end=True))


def create_horizontal(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_horizontal, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(
            plot, create_horizontal, 2, kwargs, 'xy',
            object_func=lambda pos: (TempObject(plot, ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 0, 1)), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 0, 1)), end=True))


def create_frontal(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_frontal, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(
            plot, create_frontal, 2, kwargs, 'xy',
            object_func=lambda pos: (TempObject(plot, ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1]))),
                kwargs['obj'].general_object.ag_object.normal & ag.Vector(0, 1, 0)), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Line(ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1]))),
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
            plot.print('Distance: {}'.format(ag.distance(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
        except Exception:
            try:
                plot.print('Distance: {}'.format(ag.distance(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
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
            plot.print('Angle: {}'.format(ag.angle(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
        except Exception:
            try:
                plot.print('Angle: {}'.format(ag.angle(kwargs['obj1'].general_object.ag_object, kwargs['obj'].general_object.ag_object)))
            except Exception:
                plot.print('Error')


def create_circle(plot, step, **kwargs):
    if step == 1:
        plot.print('Select plane')
        select_object(plot, create_circle, 1, kwargs, (ag.Plane,))
    elif step == 2:
        select_screen_point(plot, create_circle, 2, kwargs, 'xy', object_func=lambda pos: (
            TempObject(plot, ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                         kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                                                   plot.pm.convert_screen_y_to_ag_y(pos[1]))),
                          color=COLOR1),))
    elif step == 3:
        center = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                          plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                          kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                                                    plot.pm.convert_screen_y_to_ag_y(kwargs['c'])))
        select_screen_point(
            plot, create_circle, 3, kwargs, 'xy',
            object_func=lambda pos: (TempObject(plot, ag.Circle(center, ag.distance(center, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1])))), kwargs['obj'].general_object.ag_object.normal),
                                                   color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Circle(center, ag.distance(center, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]),
                plot.pm.convert_screen_y_to_ag_y(pos[1]),
                kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                          plot.pm.convert_screen_y_to_ag_y(pos[1])))), kwargs['obj'].general_object.ag_object.normal),
                                                   end=True))


def create_cone(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_cone, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_cone, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(plot, create_cone, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        s2 = ScreenSegment(plot, a1, b1, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(
            plot, create_cone, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                   'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 5:
        p1 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        select_screen_point(
            plot, create_cone, 5, dict(), 'xy',
            object_func=lambda pos: (TempObject(plot, ag.Cone(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), color=COLOR1),),
            final_func=lambda pos: plot.add_object(ag.Cone(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), end=True))


def create_sphere(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_sphere, 1, kwargs, 'xy')
    elif step == 2:
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_sphere, 2, {'x0': kwargs['x'], 'y': kwargs['c']}, 'xz', x=kwargs['x'],
                            c=kwargs['c'], objects=(a,))
    elif step == 3:
        center = TempObject(plot, ag.Point(
            plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
            plot.pm.convert_screen_y_to_ag_y(kwargs['y']),
            plot.pm.convert_screen_y_to_ag_z(kwargs['c'])
        ), color=COLOR1)
        select_screen_point(plot, create_sphere, 3, kwargs, 'xy', objects=(center,),
                            object_func=lambda pos: (
                                TempObject(plot, ag.Sphere(center.ag_object, ag.distance(center.ag_object, ag.Point(
                                    plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                    plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                    center.ag_object.z))),
                                              color=COLOR1),),
                            final_func=lambda pos: plot.add_object(
                                ag.Sphere(center.ag_object, ag.distance(center.ag_object, ag.Point(
                                    plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                    plot.pm.convert_screen_y_to_ag_y(pos[1]),
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
        except Exception:
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
            point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                             kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                                       plot.pm.convert_screen_y_to_ag_y(pos[1])))
            spline = point
            if len(kwargs['points']) == 1:
                spline = ag.Segment(kwargs['points'][0], point)
            elif len(kwargs['points']) > 1:
                spline = ag.Spline(kwargs['obj'].general_object.ag_object, *kwargs['points'], point)
            plot.update(TempObject(plot, point, color=COLOR1), TempObject(plot, spline, color=COLOR1))

        def mouse_left(pos):
            pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
            point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                             kwargs['obj'].general_object.ag_object.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                                       plot.pm.convert_screen_y_to_ag_y(pos[1])))
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
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=COLOR1)
        select_screen_point(plot, create_rotation_surface, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy',
                            objects=(a1,),
                            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        select_screen_point(plot, create_rotation_surface, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], COLOR1)
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], COLOR1)
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], COLOR1)
        s1 = ScreenSegment(plot, a1, a2, COLOR1)
        s2 = ScreenSegment(plot, a1, b1, COLOR_CONNECT_LINE, thickness=1, line_type=Qt.DashLine)
        select_screen_point(
            plot, create_rotation_surface, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                               'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: (ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, COLOR1),))
    elif step == 5:
        p1 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        if ag.Vector(p1, p2) | ag.Vector(0, 0, 1):
            plane = ag.Plane(p1, p2, ag.Vector(0, 1, 0) & ag.Vector(p1, p2))
            l1 = plot.pm.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xz', COLOR_CONNECT_LINE)
            l2 = plot.pm.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xz', COLOR_CONNECT_LINE)

            def mouse_move(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plane.y(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_z(pos[1])),
                                 plot.pm.convert_screen_y_to_ag_z(pos[1]))
                plot.update(TempObject(plot, point, color=COLOR1),
                            TempObject(plot, ag.Segment(p1, p2), color=COLOR1), l1, l2)

            def mouse_left(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plane.y(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_z(pos[1])),
                                 plot.pm.convert_screen_y_to_ag_z(pos[1]))
                create_rotation_surface(plot, 6, **kwargs, points=[point])

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
        else:
            plane = ag.Plane(p1, p2, ag.Vector(0, 0, 1) & ag.Vector(p1, p2))
            l1 = plot.pm.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xy', COLOR_CONNECT_LINE)
            l2 = plot.pm.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xy', COLOR_CONNECT_LINE)

            def mouse_move(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                 plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_y(pos[1])))
                plot.update(TempObject(plot, point, color=COLOR1),
                            TempObject(plot, ag.Segment(p1, p2), color=COLOR1), l1, l2)

            def mouse_left(pos):
                pos = nearest_point((pos.x(), pos.y()), l1, as_line=True)
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                 plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_y(pos[1])))
                create_rotation_surface(plot, 6, **kwargs, points=[point])

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
    elif step == 6:
        p1 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        v = ag.Vector(p1, p2) * (1 / ag.distance(p1, p2))
        if ag.Vector(p1, p2) | ag.Vector(0, 0, 1):
            plane = ag.Plane(p1, p2, ag.Vector(0, 1, 0) & ag.Vector(p1, p2))
            l1 = plot.pm.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xz', COLOR_CONNECT_LINE)
            l2 = plot.pm.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xz', COLOR_CONNECT_LINE)

            def mouse_move(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xz')
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plane.y(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_z(pos[1])),
                                 plot.pm.convert_screen_y_to_ag_z(pos[1]))

                if len(kwargs['points']) == 1:
                    spline = ag.Segment(kwargs['points'][0], point)
                else:
                    spline = ag.Spline(plane, *kwargs['points'], point)
                plot.update(TempObject(plot, point, color=COLOR1),
                            TempObject(plot, ag.Segment(p1, p2), color=COLOR1),
                            TempObject(plot, spline, color=COLOR1), l1, l2)

            def mouse_left(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xz')
                if distance(pos, nearest_point(pos, l2, as_line=True)) < 10:
                    pos = nearest_point(pos, l2, as_line=True)
                    point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                     plane.y(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                             plot.pm.convert_screen_y_to_ag_z(pos[1])),
                                     plot.pm.convert_screen_y_to_ag_z(pos[1]))
                    kwargs['points'].append(point)
                    kwargs['points'][0] += -v
                    kwargs['points'][-1] += v
                    plot.add_object(ag.RotationSurface(p1, p2, ag.Spline(plane, kwargs['points'])), end=True)
                else:
                    point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                     plane.y(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                             plot.pm.convert_screen_y_to_ag_z(pos[1])),
                                     plot.pm.convert_screen_y_to_ag_z(pos[1]))
                    kwargs['points'].append(point)
                    create_rotation_surface(plot, 6, **kwargs)

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
        else:
            plane = ag.Plane(p1, p2, ag.Vector(0, 0, 1) & ag.Vector(p1, p2))
            l1 = plot.pm.line_projections(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xy', COLOR_CONNECT_LINE)
            l2 = plot.pm.line_projections(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xy', COLOR_CONNECT_LINE)

            def mouse_move(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
                point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                 plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                 plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                         plot.pm.convert_screen_y_to_ag_y(pos[1])))

                if len(kwargs['points']) == 1:
                    spline = ag.Segment(kwargs['points'][0], point)
                else:
                    spline = ag.Spline(plane, *kwargs['points'], point)
                plot.update(TempObject(plot, point, color=COLOR1),
                            TempObject(plot, ag.Segment(p1, p2), color=COLOR1),
                            TempObject(plot, spline, color=COLOR1), l1, l2)

            def mouse_left(pos):
                pos = plot.sm.get_snap((pos.x(), pos.y()), 'xy')
                if distance(pos, nearest_point(pos, l2, as_line=True)) < 10:
                    pos = nearest_point(pos, l2, as_line=True)
                    point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                     plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                     plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                             plot.pm.convert_screen_y_to_ag_y(pos[1])))
                    kwargs['points'].append(point)
                    kwargs['points'][0] += -v
                    kwargs['points'][-1] += v
                    plot.add_object(ag.RotationSurface(p1, p2, ag.Spline(plane, kwargs['points'])), end=True)
                else:
                    point = ag.Point(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                     plot.pm.convert_screen_y_to_ag_y(pos[1]),
                                     plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]),
                                             plot.pm.convert_screen_y_to_ag_y(pos[1])))
                    kwargs['points'].append(point)
                    create_rotation_surface(plot, 6, **kwargs)

            plot.mouse_move = mouse_move
            plot.mouse_left = mouse_left
