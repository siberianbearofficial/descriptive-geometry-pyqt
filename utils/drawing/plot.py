import pygame as pg
import utils.maths.angem as ag
from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager
import utils.drawing.snap as snap
from utils.drawing.layer import Layer
from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment
from utils.drawing.screen_circle import ScreenCircle
import random


class Plot:

    POINT_SELECTION = 0
    SEGMENT_SELECTION = 1

    def __init__(self, screen, tlp, brp):
        self.screen = screen
        self.click_listening = False
        self.action = None

        self.tlp = tlp
        self.brp = brp
        self.zoom = 1

        self.bg_color = (255, 255, 255)

        self.layers = [Layer(self, 'Слой 1')]
        self.current_layer = 0

        self.axis = Axis(self)
        self.pm = ProjectionManager(self)
        self.sm = snap.SnapManager(self)

        self.clear()
        self.axis.draw()
        self.screen.update()

        # TODO: Remove this after implementing the point selection normally
        self.point_position_x = None
        self.point_position_y = None
        self.point_position_z = None

    def clear(self, index=-1):
        if index == -1:
            for layer in self.layers:
                layer.clear()
        else:
            self.layers[index].clear()
        self.full_update()
        self.screen.update()

    def draw_segment(self, segment, color=(0, 0, 0)):
        pg.draw.line(self.screen.screen, color, segment.p1.tuple(), segment.p2.tuple(), 2)

    def draw_point(self, point, color=(0, 0, 0)):
        pg.draw.circle(self.screen.screen, color, point.tuple(), 3)

    def draw_circle(self, circle, color=(0, 0, 0)):
        pg.draw.circle(self.screen.screen, color, circle.center.tuple(), circle.radius, 1)

    def draw_object(self, obj, color=(0, 0, 0)):
        print('Drawing object: {}'.format(obj))
        obj_xy = self.pm.get_projection(obj, 'xy', color)
        obj_xz = self.pm.get_projection(obj, 'xz', color)
        print('Obj_xy:', obj_xy)
        print('Obj_xz:', obj_xz)
        obj_xy.draw()
        obj_xz.draw()
        self.screen.update()

    def stop_listening(self):
        self.click_listening = False

    def start_listening(self):
        self.click_listening = True

    def point_selection(self):
        self.action = Plot.POINT_SELECTION
        self.start_listening()

    def segment_selection(self):
        self.action = Plot.SEGMENT_SELECTION
        self.start_listening()

    def clicked(self, pos):
        if self.click_listening:
            self.process_click(pos)

    def change_current_layer(self, new_layer):
        self.current_layer = new_layer
        self.screen.menu.update_layer_list()

    def add_layer(self, name):
        self.layers.append(Layer(self, name))
        self.screen.menu.update_layer_list()

    def show_hide_layer(self, hidden, index=-1):
        if index == -1:
            self.layers[self.current_layer].hidden = hidden
        else:
            self.layers[index].hidden = hidden
        self.screen.menu.update_layer_list()

    def process_click(self, pos):
        # TODO: Implement it normally! (not like this...)
        if self.action == Plot.POINT_SELECTION:
            if self.point_position_x is None:
                self.point_position_x = 640 - pos[0]
            elif self.point_position_y is None:
                self.point_position_y = pos[1] - 240
            elif self.point_position_z is None:
                self.point_position_z = 240 - pos[1]
                p = ag.Point(self.point_position_x, self.point_position_y, self.point_position_z)
                self.draw_object(p)
                self.point_position_x = None
                self.point_position_y = None
                self.point_position_z = None
        elif self.action == Plot.SEGMENT_SELECTION:
            print('Segment selection not implemented yet')

    def zoom_in(self):
        self.zoom *= 2
        self.pm.zoom *= 2
        for layer in self.layers:
            layer.update_projections()
        self.full_update()
        self.screen.menu.full_update_toolbars()

    def zoom_out(self):
        self.zoom /= 2
        self.pm.zoom /= 2
        for layer in self.layers:
            layer.update_projections()
        self.full_update()
        self.screen.menu.full_update_toolbars()

    def full_update(self):
        pg.draw.rect(self.screen.screen, self.bg_color,
                     (self.tlp[0], self.tlp[1] - 2, self.brp[0] - self.tlp[0], self.brp[1] - self.tlp[1] + 4))
        self.axis.draw()
        for layer in self.layers:
            layer.draw()

    def point_is_on_plot(self, point):
        return self.tlp[0] < point[0] < self.brp[0] and self.tlp[1] < point[1] < self.brp[1]

    @staticmethod
    def check_exit_event(event):
        if event.type == pg.QUIT:
            pg.quit()
            exit(0)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            return True
        return False

    def select_object(self, types):
        def check_object_type(obj):
            if types is None:
                return True
            if isinstance(types, tuple):
                for el in types:
                    if isinstance(obj.ag_object, el):
                        return True
                return False
            return isinstance(obj.ag_object, types)

        clock = pg.time.Clock()
        while True:
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return None
                elif event.type == pg.MOUSEBUTTONDOWN:
                    for layer in self.layers:
                        for obj in layer.objects:
                            if check_object_type(obj):
                                for el in obj.xy_projection:
                                    if isinstance(el, ScreenPoint) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenSegment) and snap.distance(
                                            pg.mouse.get_pos(), snap.nearest_point(event.pos, el)) <= 2:
                                        return obj.ag_object
                                for el in obj.xz_projection:
                                    if isinstance(el, ScreenPoint) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenSegment) and snap.distance(
                                            pg.mouse.get_pos(), snap.nearest_point(event.pos, el)) <= 2:
                                        return obj.ag_object
            clock.tick(30)

    def select_screen_point(self, plane, x=None, y=None, z=None, segment=None, objects=tuple()):
        clock = pg.time.Clock()
        c = z if plane == 'xy' else y
        while True:
            self.full_update()
            pos = self.sm.get_snap(self.screen, pg.mouse.get_pos(), plane, x=x, y=y, z=z, last_point=segment)
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return None
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                    res = self.sm.get_snap(self.screen, event.pos, plane, x=x, y=y, z=z, last_point=segment)
                    if x is None and c is None:
                        return res
                    elif x is not None:
                        return res[1]
                    else:
                        return res[0]
            if self.point_is_on_plot(pos):
                pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                if segment is not None:
                    pg.draw.line(self.screen.screen, (0, 162, 232), segment, pos, 2)
                if x is not None and c is not None:
                    pg.draw.line(self.screen.screen, (180, 180, 180), (x, c), pos, 2)
                for obj in objects:
                    obj.draw()
                self.screen.update()
                clock.tick(30)

    def create_point(self):
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a,))) is not None:
            z = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Point(self.pm.convert_screen_x_to_ag_x(x),
                                                            self.pm.convert_screen_y_to_ag_y(y),
                                           self.pm.convert_screen_y_to_ag_z(z)), random_color)
        self.full_update()
        return True

    def create_segment(self):
        if (r := self.select_screen_point('xy')) is not None:
            x1, y1 = r
        else:
            return
        a1 = ScreenPoint(self, x1, y1, (0, 162, 232))
        if (r := self.select_screen_point('xy', segment=(x1, y1), objects=(a1,))) is not None:
            x2, y2 = r
        else:
            return
        a2 = ScreenPoint(self, x2, y2, (0, 162, 232))
        s1 = ScreenSegment(self, a1, a2, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x1, y=y1, objects=(a1, a2, s1))) is not None:
            z1 = r
        else:
            return
        b1 = ScreenPoint(self, x1, z1, (0, 162, 232))
        s2 = ScreenSegment(self, a1, b1, (180, 180, 180))
        if (r := self.select_screen_point('xz', x=x2, y=y2, segment=(x1, z1), objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Segment(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), random_color)
        self.full_update()
        return True

    def create_line(self):
        if (r := self.select_screen_point('xy')) is not None:
            x1, y1 = r
        else:
            return
        a1 = ScreenPoint(self, x1, y1, (0, 162, 232))
        if (r := self.select_screen_point('xy', segment=(x1, y1), objects=(a1,))) is not None:
            x2, y2 = r
        else:
            return
        a2 = ScreenPoint(self, x2, y2, (0, 162, 232))
        s1 = ScreenSegment(self, a1, a2, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x1, y=y1, objects=(a1, a2, s1))) is not None:
            z1 = r
        else:
            return
        b1 = ScreenPoint(self, x1, z1, (0, 162, 232))
        s2 = ScreenSegment(self, a1, b1, (180, 180, 180))
        if (
        r := self.select_screen_point('xz', x=x2, y=y2, segment=(x1, z1), objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Line(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), random_color)
        self.full_update()
        return True

    def create_plane(self):
        if (r := self.select_screen_point('xy', y=self.axis.lp.y, z=self.axis.lp.y)) is not None:
            x0 = r
        else:
            return
        a = ScreenPoint(self, x0, self.axis.lp.y, (0, 162, 232))
        if (r := self.select_screen_point('xy', segment=a.tuple(), objects=(a,))) is not None:
            x1, y1 = r
        else:
            return
        b = ScreenPoint(self, x1, y1)
        h0 = ScreenSegment(self, a, b, (0, 162, 232))
        if (r := self.select_screen_point('xz', segment=a.tuple(), objects=(a, b, h0))) is not None:
            x2, z2 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Plane(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x0), 0, 0),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1), 0),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), 0, self.pm.convert_screen_y_to_ag_z(z2))), random_color)
        self.full_update()
        return True

    def create_perpendicular(self, line=False):
        # TODO: сделать так, чтобы при попытке провести перпендикуляр к горизонтали/фронтали не происходило деление на 0
        self.full_update()
        self.screen.update()
        obj = self.select_object((ag.Segment, ag.Line, ag.Plane))
        if isinstance(obj, ag.Segment):
            v = ag.Vector(obj.p1, obj.p2)
            obj = ag.Line(obj.p1, obj.p2)
        elif isinstance(obj, ag.Line):
            v = obj.vector
        elif isinstance(obj, ag.Plane):
            v = obj.normal
        else:
            return
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a,))) is not None:
            z = r
        else:
            return
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                      self.pm.convert_screen_y_to_ag_z(z))
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        if line:
            if isinstance(obj, ag.Plane):
                self.layers[self.current_layer].add_object(ag.Line(p1, v), random_color)
            else:
                self.layers[self.current_layer].add_object(ag.Line(p1, v & ag.Plane(p1, obj).normal), random_color)
        else:
            if isinstance(obj, ag.Plane):
                p2 = ag.Line(p1, v).intersection(obj)
            else:
                p2 = ag.Line(p1, v & ag.Plane(p1, obj).normal).intersection(obj)
            if p2 is None:
                print('error: can\'t create perpendicular')
                return
            self.layers[self.current_layer].add_object(ag.Segment(p1, p2), random_color)
        self.full_update()
        return True

    def create_parallel(self, line=False):
        # TODO: для отрезков сделать возможность указазывать вторую точку
        self.full_update()
        self.screen.update()
        obj = self.select_object((ag.Segment, ag.Line))
        if isinstance(obj, ag.Segment):
            v = ag.Vector(obj.p1, obj.p2)
            obj = ag.Line(obj.p1, obj.p2)
        elif isinstance(obj, ag.Line):
            v = obj.vector
        else:
            return
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a,))) is not None:
            z = r
        else:
            return
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                      self.pm.convert_screen_y_to_ag_z(z))
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        if line:
            self.layers[self.current_layer].add_object(ag.Line(p1, v), random_color)
        else:
            self.layers[self.current_layer].add_object(ag.Segment(p1, p1 + v), random_color)
        self.full_update()
        return True

    def create_plot_from_3_points(self):
        if (r := self.select_screen_point('xy')) is not None:
            x1, y1 = r
        else:
            return
        a1 = ScreenPoint(self, x1, y1, (0, 162, 232))
        if (r := self.select_screen_point('xy', segment=(x1, y1), objects=(a1,))) is not None:
            x2, y2 = r
        else:
            return
        a2 = ScreenPoint(self, x2, y2, (0, 162, 232))
        s1 = ScreenSegment(self, a1, a2, (0, 162, 232))
        if (r := self.select_screen_point('xy', segment=(x2, y2), objects=(a1, a2, s1))) is not None:
            x3, y3 = r
        else:
            return
        a3 = ScreenPoint(self, x3, y3, (0, 162, 232))
        s2 = ScreenSegment(self, a2, a3, (0, 162, 232))
        s3 = ScreenSegment(self, a1, a3, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x1, y=y1, objects=(a1, a2, a3, s1, s2, s3))) is not None:
            z1 = r
        else:
            return
        b1 = ScreenPoint(self, x1, z1, (0, 162, 232))
        l1 = ScreenSegment(self, a1, b1, (180, 180, 180))
        if (r := self.select_screen_point('xz', x=x2, y=y2, segment=(x1, z1),
                                          objects=(a1, a2, a3, s1, s2, s3, b1, l1))) is not None:
            z2 = r
        else:
            return
        b2 = ScreenPoint(self, x2, z2, (0, 162, 232))
        l2 = ScreenSegment(self, a2, b2, (180, 180, 180))
        c = ScreenSegment(self, b1, b2, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x3, y=y3, segment=(x2, z2),
                                          objects=(a1, a2, a3, s1, s2, s3, b1, b2, l1, l2, c))) is not None:
            z3 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Plane(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x3), self.pm.convert_screen_y_to_ag_y(y3),
                     self.pm.convert_screen_y_to_ag_z(z3))), random_color)
        self.full_update()
        return True

    def create_parallel_plane(self):
        self.full_update()
        self.screen.update()
        obj = self.select_object(ag.Plane)
        if obj is None:
            return
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a,))) is not None:
            z = r
        else:
            return
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                      self.pm.convert_screen_y_to_ag_z(z))
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Plane(obj.normal, p1), random_color)
        self.full_update()
        return True

    def create_h_f(self, f=False):
        self.full_update()
        self.screen.update()
        obj = self.select_object(ag.Plane)
        if obj is None:
            return
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a,))) is not None:
            z = r
        else:
            return
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                      self.pm.convert_screen_y_to_ag_z(z))
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[self.current_layer].add_object(ag.Line(
            p1, obj.normal & (ag.Vector(0, 1, 0) if f else ag.Vector(0, 0, 1))), random_color)
        self.full_update()
        return True

    def get_distance(self):
        if (r := self.select_object(None)) is None:
            return
        else:
            obj1 = r
        if (r := self.select_object(None)) is None:
            return
        else:
            obj2 = r
        try:
            print(ag.distance(obj1, obj2))
        except Exception:
            print('Ошибка')

    def get_angle(self):
        if (r := self.select_object(None)) is None:
            return
        else:
            obj1 = r
        if (r := self.select_object(None)) is None:
            return
        else:
            obj2 = r
        try:
            print(ag.angle(obj1, obj2))
        except Exception:
            print('Ошибка')
