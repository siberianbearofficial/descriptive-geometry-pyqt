from utils.drawing.screen_point import ScreenPoint, ScreenPoint2
from utils.drawing.screen_segment import ScreenSegment
from utils.drawing.screen_circle import ScreenCircle
from utils.drawing.general_object import GeneralObject
import utils.maths.angem as ag


def select_screen_point(plot, func, step, kwargs, plane, x=None, c=None, objects=tuple(), object_func=None,
                        final_func=None):
    if plane == 'xy':
        y, z = None, c
    else:
        y, z = c, None

    def mouse_move(pos):
        pos = plot.sm.get_snap((pos.x(), pos.y()), plane, x=x, y=y, z=z)
        if c is not None:
            if object_func:
                plot.update(ScreenPoint(plot, *pos, color=(0, 162, 232)),
                            ScreenSegment(plot, (x, c), pos, color=(180, 180, 180)), object_func(pos), *objects)
            else:
                plot.update(ScreenPoint(plot, *pos, color=(0, 162, 232)),
                            ScreenSegment(plot, (x, c), pos, color=(180, 180, 180)), *objects)
        elif object_func:
            plot.update(ScreenPoint(plot, *pos, color=(0, 162, 232)), object_func(pos), *objects)
        else:
            plot.update(ScreenPoint(plot, *pos, color=(0, 162, 232)), *objects)

    def mouse_left(pos):
        pos = plot.sm.get_snap((pos.x(), pos.y()), plane, x=x, y=y, z=z)
        if final_func:
            final_func(pos)
        else:
            func(plot, step + 1, **kwargs, x=pos[0], c=pos[1])

    plot.mouse_move = mouse_move
    plot.mouse_left = mouse_left
    plot.mouse_right = lambda pos: plot.end()


def create_point(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_point, 1, kwargs, 'xy')
    elif step == 2:
        a = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=(0, 162, 232))
        select_screen_point(plot, create_point, 2, kwargs, 'xz', x=kwargs['x'], c=kwargs['c'], objects=(a,),
                            final_func=lambda pos: plot.add_object(ag.Point(
                                plot.pm.convert_screen_x_to_ag_x(kwargs['x']),
                                plot.pm.convert_screen_y_to_ag_y(kwargs['c']),
                                plot.pm.convert_screen_y_to_ag_z(pos[1])
                            ), end=True))


def create_segment(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_segment, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=(0, 162, 232))
        select_screen_point(plot, create_segment, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, (0, 162, 232)))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], (0, 162, 232))
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], (0, 162, 232))
        s1 = ScreenSegment(plot, a1, a2, (0, 162, 232))
        select_screen_point(plot, create_segment, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], (0, 162, 232))
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], (0, 162, 232))
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], (0, 162, 232))
        s1 = ScreenSegment(plot, a1, a2, (0, 162, 232))
        s2 = ScreenSegment(plot, a1, b1, (180, 180, 180))
        select_screen_point(
            plot, create_segment, 3, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                      'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, (0, 162, 232)),
            final_func=lambda pos: plot.add_object(ag.Segment(
                ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                         plot.pm.convert_screen_y_to_ag_z(kwargs['c'])),
                ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                         plot.pm.convert_screen_y_to_ag_z(pos[1]))
            ), end=True))


def create_cylinder(plot, step, **kwargs):
    if step == 1:
        select_screen_point(plot, create_cylinder, 1, kwargs, 'xy')
    elif step == 2:
        a1 = ScreenPoint(plot, kwargs['x'], kwargs['c'], color=(0, 162, 232))
        select_screen_point(plot, create_cylinder, 2, {'x1': kwargs['x'], 'y1': kwargs['c']}, 'xy', objects=(a1,),
                            object_func=lambda pos: ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, (0, 162, 232)))
    elif step == 3:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], (0, 162, 232))
        a2 = ScreenPoint(plot, kwargs['x'], kwargs['c'], (0, 162, 232))
        s1 = ScreenSegment(plot, a1, a2, (0, 162, 232))
        select_screen_point(plot, create_cylinder, 3,
                            {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x'], 'y2': kwargs['c']},
                            'xz', x=kwargs['x1'], c=kwargs['y1'], objects=(a1, a2, s1))
    elif step == 4:
        a1 = ScreenPoint(plot, kwargs['x1'], kwargs['y1'], (0, 162, 232))
        a2 = ScreenPoint(plot, kwargs['x2'], kwargs['y2'], (0, 162, 232))
        b1 = ScreenPoint(plot, kwargs['x1'], kwargs['c'], (0, 162, 232))
        s1 = ScreenSegment(plot, a1, a2, (0, 162, 232))
        s2 = ScreenSegment(plot, a1, b1, (180, 180, 180))
        select_screen_point(
            plot, create_cylinder, 4, {'x1': kwargs['x1'], 'y1': kwargs['y1'], 'x2': kwargs['x2'],
                                       'y2': kwargs['y2'], 'z1': kwargs['c']},
            'xz', x=kwargs['x2'], c=kwargs['y2'], objects=(a1, a2, s1, s2, b1),
            object_func=lambda pos: ScreenSegment(plot, (kwargs['x'], kwargs['c']), pos, (0, 162, 232)))
    elif step == 5:
        print('---------------------- step 5 ---------------------')
        p1 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x1']), plot.pm.convert_screen_y_to_ag_y(kwargs['y1']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['z1']))
        p2 = ag.Point(plot.pm.convert_screen_x_to_ag_x(kwargs['x2']), plot.pm.convert_screen_y_to_ag_y(kwargs['y2']),
                      plot.pm.convert_screen_y_to_ag_z(kwargs['c']))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        select_screen_point(
            plot, create_cylinder, 5, dict(), 'xy',
            object_func=lambda pos: GeneralObject(plot, ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), color=(0, 162, 232)),
            final_func=lambda pos: plot.add_object(ag.Cylinder(p1, p2, ag.distance(p1, ag.Point(
                plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]),
                plane.z(plot.pm.convert_screen_x_to_ag_x(pos[0]), plot.pm.convert_screen_y_to_ag_y(pos[1]))
            ))), end=True))
