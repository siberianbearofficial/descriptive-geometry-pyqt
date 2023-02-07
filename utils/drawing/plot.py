import pygame as pg
import utils.maths.angem as ag
from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager
import utils.drawing.snap as snap
from utils.drawing.layer import Layer
from utils.drawing.screen_point import ScreenPoint, ScreenPoint2
from utils.drawing.screen_segment import ScreenSegment
from utils.drawing.screen_circle import ScreenCircle
from utils.drawing.general_object import GeneralObject
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
        self.camera_pos = (0, 0)
        self.clock = pg.time.Clock()

        self.bg_color = (255, 255, 255)

        self.layers = [Layer(self, 'Слой 1')]
        self.current_layer = 0
        self.selected_object = None
        self.selected_object_index = None

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

        self.serializable = ['bg_color', 'layers', 'current_layer']

    def clear(self, index=-1):
        if index == -1:
            for layer in self.layers:
                layer.clear()
        else:
            self.layers[index].clear()
            self.sm.update_intersections()
        self.full_update()
        self.screen.update()

    def update(self, bg_color, layers):
        self.bg_color = bg_color
        self.layers = layers
        self.full_update()

    def resize(self, tlp, brp):
        self.tlp = tlp
        self.brp = brp
        pg.draw.rect(self.screen.screen, self.bg_color,
                     (self.tlp[0], self.tlp[1] - 2, self.brp[0] - self.tlp[0], self.brp[1] - self.tlp[1] + 4))
        self.axis.update(self)
        self.axis.draw()
        for layer in self.layers:
            layer.update_projections()
            layer.draw()
        self.screen.update()

    def draw_segment(self, segment, color=(0, 0, 0)):
        # if self.tlp[0] <= segment.p1.x <= self.brp[0] and self.tlp[1] <= segment.p1.y <= self.brp[1] \
        #         or self.tlp[0] <= segment.p2.x <= self.brp[0] and self.tlp[1] <= segment.p2.y <= self.brp[1]:
        pg.draw.line(self.screen.screen, color, segment.point1.tuple(), segment.point2.tuple(), 2)

    def draw_point(self, point, color=(0, 0, 0)):
        if self.tlp[0] + 3 <= point.x <= self.brp[0] - 3 and self.tlp[1] + 3 <= point.y <= self.brp[1] - 3:
            pg.draw.circle(self.screen.screen, color, point.tuple(), 3)

    def draw_point2(self, point, color=(0, 0, 0)):
        if self.tlp[0] + 1 <= point.x <= self.brp[0] - 1 and self.tlp[1] + 1 <= point.y <= self.brp[1] - 1:
            pg.draw.circle(self.screen.screen, color, point.tuple(), 1)

    def draw_circle(self, circle, color=(0, 0, 0)):
        if self.tlp[0] + circle.radius + 1 <= circle.center.x <= self.brp[0] - circle.radius - 1 \
                and self.tlp[1] + circle.radius + 1 <= circle.center.y <= self.brp[1] - circle.radius - 1:
            pg.draw.circle(self.screen.screen, color, circle.center.tuple(), circle.radius, 2)

    def draw_object(self, obj, color=(0, 0, 0)):
        print('Drawing object: {}'.format(obj))
        obj_xy = self.pm.get_projection(obj, 'xy', color)
        obj_xz = self.pm.get_projection(obj, 'xz', color)
        print('Obj_xy:', obj_xy)
        print('Obj_xz:', obj_xz)
        obj_xy.draw()
        obj_xz.draw()
        self.screen.update()

    def move_camera(self, x, y):
        self.axis.move(0, y)
        self.camera_pos = self.camera_pos[0] + x, self.camera_pos[1] + y
        self.pm.camera_pos = self.camera_pos
        for layer in self.layers:
            layer.move_objects(x, y)
            # layer.update_projections()
        self.sm.update_intersections()
        self.full_update()
        self.screen.update()

    def moving_camera(self):
        pos = pg.mouse.get_pos()
        while True:
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 3:
                        return
                    if event.button == 4:
                        self.zoom_in()
                    elif event.button == 5:
                        self.zoom_out()
            p = pg.mouse.get_pos()
            self.move_camera(p[0] - pos[0], p[1] - pos[1])
            pos = p
            self.clock.tick(60)

    def clicked(self, pos):
        old_obj = self.selected_object
        self.selected_object, self.selected_object_index = None, None
        for i in range(len(self.layers)):
            if self.layers[i].hidden:
                continue
            for j in range(len(self.layers[i].objects)):
                obj = self.layers[i].objects[j]
                for el in obj.xy_projection:
                    if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 4:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenPoint2) and snap.distance(pos, el.tuple()) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenSegment) and snap.distance(
                            pg.mouse.get_pos(), snap.nearest_point(pos, el)) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center.tuple()) - el.radius) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                for el in obj.xz_projection:
                    if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 2:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenPoint2) and snap.distance(pos, el.tuple()) <= 2:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenSegment) and snap.distance(
                            pg.mouse.get_pos(), snap.nearest_point(pos, el)) <= 2:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center.tuple()) - el.radius) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
        if self.selected_object is not None:
            for el in self.selected_object.xy_projection:
                if isinstance(el, ScreenPoint) and \
                        self.tlp[0] + 3 <= el.x <= self.brp[0] - 3 and self.tlp[1] + 3 <= el.y <= self.brp[1] - 3:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.tuple(), 6)
                elif isinstance(el, ScreenPoint2) and \
                        self.tlp[0] + 1 <= el.x <= self.brp[0] - 1 and self.tlp[1] + 1 <= el.y <= self.brp[1] - 1:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.tuple(), 2)
                elif isinstance(el, ScreenSegment) and el.drawing:
                    pg.draw.line(self.screen.screen, (0, 162, 232), el.point1.tuple(), el.point2.tuple(), 4)
                    # pg.draw.circle(self.screen.screen, (0, 162, 232), el.p1.tuple(), 4)
                    # pg.draw.circle(self.screen.screen, (0, 162, 232), el.p2.tuple(), 4)
                elif isinstance(el, ScreenCircle) and self.tlp[0] + el.radius + 1 <= el.center.x <= self.brp[0] - \
                        el.radius - 1 and self.tlp[1] + el.radius + 1 <= el.center.y <= self.brp[1] - el.radius - 1:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.center.tuple(), el.radius + 1, 4)
            for el in self.selected_object.xz_projection:
                if isinstance(el, ScreenPoint) and \
                        self.tlp[0] + 3 <= el.x <= self.brp[0] - 3 and self.tlp[1] + 3 <= el.y <= self.brp[1] - 3:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.tuple(), 6)
                elif isinstance(el, ScreenPoint2) and \
                        self.tlp[0] + 1 <= el.x <= self.brp[0] - 1 and self.tlp[1] + 1 <= el.y <= self.brp[1] - 1:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.tuple(), 2)
                elif isinstance(el, ScreenSegment) and el.drawing:
                    pg.draw.line(self.screen.screen, (0, 162, 232), el.point1.tuple(), el.point2.tuple(), 4)
                    # pg.draw.circle(self.screen.screen, (0, 162, 232), el.p1.tuple(), 4)
                    # pg.draw.circle(self.screen.screen, (0, 162, 232), el.p2.tuple(), 4)
                elif isinstance(el, ScreenCircle) and self.tlp[0] + el.radius + 1 <= el.center.x <= self.brp[0] - \
                        el.radius - 1 and self.tlp[1] + el.radius + 1 <= el.center.y <= self.brp[1] - el.radius - 1:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), el.center.tuple(), el.radius + 1, 4)
            self.selected_object.draw()

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

    def zoom_in(self):
        self.zoom *= 1.5
        self.pm.zoom *= 1.5
        for layer in self.layers:
            layer.update_projections()
        self.sm.update_intersections()
        self.full_update()

    def zoom_out(self):
        self.zoom /= 1.5
        self.pm.zoom /= 1.5
        for layer in self.layers:
            layer.update_projections()
        self.sm.update_intersections()
        self.full_update()

    def full_update(self):
        pg.draw.rect(self.screen.screen, self.bg_color,
                     (self.tlp[0], self.tlp[1], self.brp[0] - self.tlp[0], self.brp[1] - self.tlp[1]))
        # if self.tlp[0] <= self.axis.lp.x <= self.brp[0] and self.tlp[1] <= self.axis.lp.y <= self.brp[1]:
        self.axis.draw()
        for layer in self.layers:
            layer.draw()

    def point_is_on_plot(self, point):
        return self.tlp[0] < point[0] < self.brp[0] and self.tlp[1] < point[1] < self.brp[1]

    @staticmethod
    def random_color():
        red = random.randint(20, 240)
        green = random.randint(20, 240)
        blue = random.randint(20, min(570 - red - green, 240))
        return red, green, blue
        while True:
            red = random.randint(20, 240)
            green = random.randint(20, 240)
            blue = random.randint(20, 570 - red - green)
            if 300 < red + green + blue < 570:
                return red, green, blue

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

        while True:
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return None
                elif event.type == pg.MOUSEBUTTONDOWN:
                    for layer in self.layers:
                        if layer.hidden:
                            continue
                        for obj in layer.objects:
                            if check_object_type(obj):
                                for el in obj.xy_projection:
                                    if isinstance(el, ScreenPoint) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenPoint2) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenSegment) and snap.distance(
                                            pg.mouse.get_pos(), snap.nearest_point(event.pos, el)) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenCircle) and el.radius - 2 <= \
                                            snap.distance(event.pos, el.center.tuple()) <= el.radius + 2:
                                        return obj.ag_object
                                for el in obj.xz_projection:
                                    if isinstance(el, ScreenPoint) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenPoint2) and snap.distance(event.pos, el.tuple()) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenSegment) and snap.distance(
                                            pg.mouse.get_pos(), snap.nearest_point(event.pos, el)) <= 2:
                                        return obj.ag_object
                                    if isinstance(el, ScreenCircle) and el.radius - 2 <= \
                                            snap.distance(event.pos, el.center.tuple()) <= el.radius + 2:
                                        return obj.ag_object
            self.clock.tick(30)

    def select_screen_point(self, plane, x=None, y=None, z=None, segment=None, func=None, objects=tuple(), line=None):
        c = z if plane == 'xy' else y
        while True:
            self.full_update()
            if line is None:
                pos = self.sm.get_snap(self.screen, pg.mouse.get_pos(), plane, x=x, y=y, z=z, last_point=segment)
            else:
                pos = snap.nearest_point(pg.mouse.get_pos(), line, as_line=True)
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return None
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                    if line is None:
                        res = self.sm.get_snap(self.screen, event.pos, plane, x=x, y=y, z=z, last_point=segment)
                    else:
                        res = snap.nearest_point(pg.mouse.get_pos(), line, as_line=True)
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
                if func is not None:
                    func(pos)
                if x is not None and c is not None:
                    pg.draw.line(self.screen.screen, (180, 180, 180), (x, c), pos, 2)
                for obj in objects:
                    obj.draw()
                self.screen.update()
                self.clock.tick(30)

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
        self.layers[self.current_layer].add_object(ag.Point(self.pm.convert_screen_x_to_ag_x(x),
                                                            self.pm.convert_screen_y_to_ag_y(y),
                                                            self.pm.convert_screen_y_to_ag_z(z)), Plot.random_color())
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
        if (
        r := self.select_screen_point('xz', x=x2, y=y2, segment=(x1, z1), objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        self.layers[self.current_layer].add_object(ag.Segment(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), Plot.random_color())
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
                r := self.select_screen_point('xz', x=x2, y=y2, segment=(x1, z1),
                                              objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        self.layers[self.current_layer].add_object(ag.Line(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), Plot.random_color())
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
        self.layers[self.current_layer].add_object(ag.Plane(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x0), 0, 0),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1), 0),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), 0, self.pm.convert_screen_y_to_ag_z(z2))), Plot.random_color())
        self.full_update()
        return True

    def create_perpendicular(self, line=False):
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
        if line:
            if isinstance(obj, ag.Plane):
                self.layers[self.current_layer].add_object(ag.Line(p1, v), Plot.random_color())
            else:
                self.layers[self.current_layer].add_object(ag.Line(p1, v & ag.Plane(p1, obj).normal), Plot.random_color())
        else:
            if isinstance(obj, ag.Plane):
                p2 = ag.Line(p1, v).intersection(obj)
            else:
                p2 = ag.Line(p1, v & ag.Plane(p1, obj).normal).intersection(obj)
            if p2 is None:
                print('error: can\'t create perpendicular')
                return
            self.layers[self.current_layer].add_object(ag.Segment(p1, p2), Plot.random_color())
        self.full_update()
        return True

    def create_parallel(self, line=False):
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
        if line:
            self.layers[self.current_layer].add_object(ag.Line(p1, v), Plot.random_color())
        else:
            line = self.pm.get_projection(ag.Line(p1, v), 'xy', (255, 255, 255))
            if (r := self.select_screen_point('xy', line=line, segment=(x, y))) is not None:
                x2, y2 = r
            else:
                return
            p2 = ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                          ag.Line(p1, v).z((self.pm.convert_screen_x_to_ag_x(x2))))
            self.layers[self.current_layer].add_object(ag.Segment(p1, p2), Plot.random_color())
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
        self.layers[self.current_layer].add_object(ag.Plane(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x3), self.pm.convert_screen_y_to_ag_y(y3),
                     self.pm.convert_screen_y_to_ag_z(z3))), Plot.random_color())
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
        self.layers[self.current_layer].add_object(ag.Plane(obj.normal, p1), Plot.random_color())
        self.full_update()
        return True

    def create_h_f(self, f=False):
        self.full_update()
        self.screen.update()
        obj = self.select_object(ag.Plane)
        if obj is None:
            return
        if (r := self.select_screen_point('xy', func=lambda pos: pg.draw.circle(
                self.screen.screen, (0, 162, 232), self.pm.convert_ag_coordinate_to_screen_coordinate(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), 0, obj.z(
                        x=self.pm.convert_screen_x_to_ag_x(pos[0]), y=self.pm.convert_screen_y_to_ag_y(pos[1])),
                    'xz'), 3))) is not None:
            x, y = r
            z = self.pm.convert_ag_coordinate_to_screen_coordinate(
                x, y, obj.z(x=self.pm.convert_screen_x_to_ag_x(x), y=self.pm.convert_screen_y_to_ag_y(y)), 'xz')[1]
        else:
            return
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                      self.pm.convert_screen_y_to_ag_z(z))
        self.layers[self.current_layer].add_object(ag.Line(
            p1, obj.normal & (ag.Vector(0, 1, 0) if f else ag.Vector(0, 0, 1))), Plot.random_color())
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

    def get_angle(self, plane=''):
        self.full_update()
        self.screen.update()
        if (r := self.select_object(None)) is None:
            return
        else:
            obj1 = r
        if plane == '':
            if (r := self.select_object(None)) is None:
                return
            else:
                obj2 = r
            try:
                print(ag.angle(obj1, obj2))
            except Exception:
                print('Ошибка')
        elif plane == 'xy':
            try:
                print(ag.angle(obj1, ag.Plane(ag.Vector(0, 0, 1), ag.Point(0, 0, 0))))
            except Exception:
                print('Ошибка')
        elif plane == 'xz':
            try:
                print(ag.angle(obj1, ag.Plane(ag.Vector(0, 1, 0), ag.Point(0, 0, 0))))
            except Exception:
                print('Ошибка')

    def get_distance_between_points(self):
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
        print(ag.distance(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))))
        self.full_update()
        return True

    def create_circle(self):
        plane = self.select_object(ag.Plane)
        if plane is None:
            return
        if (r := self.select_screen_point('xy', func=lambda pos: pg.draw.circle(
                self.screen.screen, (0, 162, 232), self.pm.convert_ag_coordinate_to_screen_coordinate(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), 0, plane.z(
                        x=self.pm.convert_screen_x_to_ag_x(pos[0]), y=self.pm.convert_screen_y_to_ag_y(pos[1])),
                    'xz'), 3))) is not None:
            x, y = r
            z = self.pm.convert_ag_coordinate_to_screen_coordinate(
                x, y, plane.z(x=self.pm.convert_screen_x_to_ag_x(x), y=self.pm.convert_screen_y_to_ag_y(y)), 'xz')[1]
        else:
            return
        a1 = ScreenPoint(self, x, y, (0, 162, 232))
        a2 = ScreenPoint(self, x, z, (0, 162, 232))
        center = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                          self.pm.convert_screen_y_to_ag_z(z))
        if (r := self.select_screen_point('xy', objects=(a1, a2), func=lambda pos: GeneralObject(
                self, ag.Circle(center, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                    plane.z(x=self.pm.convert_screen_x_to_ag_x(pos[0]), y=self.pm.convert_screen_y_to_ag_y(pos[1]))),
                    center), plane.normal), (0, 162, 232)).draw())) is not None:
            x0, y0 = r
        else:
            return
        self.layers[self.current_layer].add_object(ag.Circle(
            center, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0),
                    plane.z(self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0))),
                    center), plane.normal), Plot.random_color())
        self.full_update()
        return True

    def create_cone(self, cylinder=False):
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
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                      self.pm.convert_screen_y_to_ag_z(z1))
        p2 = ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                      self.pm.convert_screen_y_to_ag_z(z2))
        plane = ag.Plane(ag.Vector(p1, p2), p1)
        if cylinder:
            obj_type = ag.Cylinder
        else:
            obj_type = ag.Cone
        if (r := self.select_screen_point('xy', objects=(a1, a2), func=lambda pos: GeneralObject(
                self, obj_type(p1, p2, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                    plane.z(x=self.pm.convert_screen_x_to_ag_x(pos[0]), y=self.pm.convert_screen_y_to_ag_y(pos[1]))
                    if p1.z != p2.z else p1.z),
                    p1)), (0, 162, 232)).draw())) is not None:
            x0, y0 = r
        else:
            return
        radius = ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0),
                    plane.z(self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0))
                    if p1.z != p2.z else p1.z), p1)
        self.layers[self.current_layer].add_object(obj_type(p1, p2, radius), Plot.random_color())
        self.full_update()
        return True

    def create_spline(self):
        plane = self.select_object(ag.Plane)
        if plane is None:
            return
        while True:
            points = []
            while True:
                self.full_update()
                pos = self.sm.get_snap(self.screen, pg.mouse.get_pos(), 'xy')
                events = pg.event.get()
                for event in events:
                    if Plot.check_exit_event(event):
                        return None
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                        res = self.sm.get_snap(self.screen, event.pos, 'xy')
                        points.append(ag.Point(self.pm.convert_screen_x_to_ag_x(res[0]),
                                               self.pm.convert_screen_y_to_ag_y(res[1]),
                                               plane.z(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                       self.pm.convert_screen_y_to_ag_y(res[1]))))
                    elif event.type == pg.KEYDOWN and event.key == 13:
                        self.layers[self.current_layer].add_object(ag.Spline(plane, *points), Plot.random_color())
                        self.full_update()
                        return True
                if self.point_is_on_plot(pos):
                    pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                    if len(points) == 1:
                        GeneralObject(self, ag.Segment(points[0], ag.Point(
                            self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                            plane.z(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                    self.pm.convert_screen_y_to_ag_y(pos[1])))), (0, 162, 232)).draw()
                    elif len(points) >= 2:
                        try:
                            GeneralObject(self, ag.Spline(plane, *points, ag.Point(
                            self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                            plane.z(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                    self.pm.convert_screen_y_to_ag_y(pos[1])))), (0, 162, 232)).draw()
                        except Exception:
                            pass
                    self.screen.update()
                    self.clock.tick(30)

    def get_intersection(self):
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        if (r := self.select_object(None)) is None:
            return
        else:
            obj1 = r
        print('Выберите 2-ой объект')
        if (r := self.select_object(None)) is None:
            return
        else:
            obj2 = r
        res = obj1.intersection(obj2)
        try:
            res = obj1.intersection(obj2)
        except Exception:
            try:
                res = obj1.intersection(obj2)
            except Exception:
                res = None
                print('Ошибка')
        if res is not None:
            if isinstance(res, tuple):
                for el in res:
                    self.layers[self.current_layer].add_object(el, random_color)
            else:
                self.layers[self.current_layer].add_object(res, random_color)
            print('Готово')
        else:
            print('Нет пересечения')
        self.full_update()
        return True

    def create_tor(self):
        def draw_tor(pos):
            try:
                GeneralObject(
                    self, ag.Tor(center, radius, abs(radius - ag.distance(
                    ag.Point(self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                    center.z), center)), vector), (0, 162, 232)).draw()
            except Exception:
                pass

        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a1 = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a1,))) is not None:
            z = r
        else:
            return
        a2 = ScreenPoint(self, x, z, (0, 162, 232))
        center = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                          self.pm.convert_screen_y_to_ag_z(z))
        if (r := self.select_screen_point('xy', func=lambda pos: GeneralObject(
                self, ag.Circle(center, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                    center.z), center)),
                (0, 162, 232)).draw())) is not None:
            x0, y0 = r
        else:
            return
        radius = ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0), center.z), center)
        if (r := self.select_screen_point('xy', func=lambda pos: GeneralObject(
                self, ag.Circle(center, radius, ag.Vector(center, ag.Point(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]), 0))),
                (0, 162, 232)).draw())) is not None:
            x0, y0 = r
        else:
            return
        if (r := self.select_screen_point('xz', x=x0, y=y0, func=lambda pos: GeneralObject(
                self, ag.Circle(center, radius, ag.Vector(center, ag.Point(
                    self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0),
                    self.pm.convert_screen_y_to_ag_z(pos[1])))), (0, 162, 232)).draw())) is not None:
            z0 = r
        else:
            return
        vector = ag.Vector(center, ag.Point(self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0),
                           self.pm.convert_screen_y_to_ag_z(z0)))
        if (r := self.select_screen_point('xy', func=draw_tor)) is not None:
            x0, y0 = r
        else:
            return
        tube_radius = abs(radius - ag.distance(ag.Point(
            self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0), center.z), center))
        self.layers[self.current_layer].add_object(ag.Tor(center, radius, tube_radius, vector), Plot.random_color())
        self.full_update()
        return True

    def create_rotation_surface(self):
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
        b2 = ScreenPoint(self, x2, z2, (0, 162, 232))
        p1 = ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                      self.pm.convert_screen_y_to_ag_z(z1))
        p2 = ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                      self.pm.convert_screen_y_to_ag_z(z2))
        if ag.Vector(p1, p2) | ag.Vector(0, 0, 1):
            plane = ag.Plane(p1, p2, ag.Vector(0, 1, 0) & ag.Vector(p1, p2))
            l1 = self.pm.get_projection(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xz', (200, 200, 200))
            l2 = self.pm.get_projection(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xz', (200, 200, 200))
            s2 = ScreenSegment(self, b1, b2, (0, 162, 232))
            if (r := self.select_screen_point('xz', line=l1, objects=(s1, s2, l1, l2))) is not None:
                x1, z1 = r
            else:
                return
            points = [ag.Point(self.pm.convert_screen_x_to_ag_x(x1), plane.y(x=self.pm.convert_screen_x_to_ag_x(x1),
                                       z=self.pm.convert_screen_y_to_ag_z(z1)), self.pm.convert_screen_y_to_ag_z(z1)) +
                      ag.Vector(p1, p2) * (-1 / abs(ag.Vector(p1, p2)))]
            while True:
                while True:
                    self.full_update()
                    pos = self.sm.get_snap(self.screen, pg.mouse.get_pos(), 'xz')
                    events = pg.event.get()
                    for event in events:
                        if Plot.check_exit_event(event):
                            return None
                        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                            res = self.sm.get_snap(self.screen, event.pos, 'xz')
                            if snap.distance(res, snap.nearest_point(res, l2, as_line=True)) <= 10:
                                res = snap.nearest_point(res, l2, as_line=True)
                                points.append(ag.Point(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                       plane.y(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                               self.pm.convert_screen_y_to_ag_z(res[1])),
                                                       self.pm.convert_screen_y_to_ag_z(res[1])) +
                                              ag.Vector(p1, p2) * (1 / abs(ag.Vector(p1, p2))))
                                self.layers[self.current_layer].add_object(
                                    ag.RotationSurface(p1, p2, ag.Spline(plane, *points)), Plot.random_color())
                                self.full_update()
                                return True
                            points.append(ag.Point(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                   plane.y(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                           self.pm.convert_screen_y_to_ag_z(res[1])),
                                                   self.pm.convert_screen_y_to_ag_z(res[1])))
                    if self.point_is_on_plot(pos):
                        pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                        if len(points) == 1:
                            GeneralObject(self, ag.Segment(points[0], ag.Point(
                                self.pm.convert_screen_x_to_ag_x(pos[0]),
                                plane.y(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                        self.pm.convert_screen_y_to_ag_z(pos[1])),
                                self.pm.convert_screen_y_to_ag_z(pos[1]))), (0, 162, 232)).draw()
                        elif len(points) >= 2:
                            try:
                                GeneralObject(self, ag.Spline(plane, *points, ag.Point(
                                    self.pm.convert_screen_x_to_ag_x(pos[0]),
                                    plane.y(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                            self.pm.convert_screen_y_to_ag_z(pos[1])),
                                    self.pm.convert_screen_y_to_ag_z(pos[1]))), (0, 162, 232)).draw()
                            except Exception:
                                pass
                        s1.draw()
                        s2.draw()
                        l1.draw()
                        l2.draw()
                        self.screen.update()
                        self.clock.tick(30)
        plane = ag.Plane(p1, p2, ag.Vector(0, 0, 1) & ag.Vector(p1, p2))
        l1 = self.pm.get_projection(ag.Line(p1, ag.Vector(p1, p2) & plane.normal), 'xy', (200, 200, 200))
        l2 = self.pm.get_projection(ag.Line(p2, ag.Vector(p1, p2) & plane.normal), 'xy', (200, 200, 200))
        s2 = ScreenSegment(self, b1, b2, (0, 162, 232))
        if (r := self.select_screen_point('xy', line=l1, objects=(s1, s2, l1, l2))) is not None:
            x1, y1 = r
        else:
            return
        points = [ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                           plane.z(x=self.pm.convert_screen_x_to_ag_x(x1), y=self.pm.convert_screen_y_to_ag_y(y1))) +
                  ag.Vector(p1, p2) * (-1 / abs(ag.Vector(p1, p2)))]
        while True:
            while True:
                self.full_update()
                pos = self.sm.get_snap(self.screen, pg.mouse.get_pos(), 'xy')
                events = pg.event.get()
                for event in events:
                    if Plot.check_exit_event(event):
                        return None
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                        res = self.sm.get_snap(self.screen, event.pos, 'xy')
                        if snap.distance(res, snap.nearest_point(res, l2, as_line=True)) <= 10:
                            res = snap.nearest_point(res, l2, as_line=True)
                            points.append(ag.Point(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                   self.pm.convert_screen_y_to_ag_y(res[1]),
                                                   plane.z(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                           self.pm.convert_screen_y_to_ag_y(res[1]))) +
                                          ag.Vector(p1, p2) * (1 / abs(ag.Vector(p1, p2))))
                            random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
                            self.layers[self.current_layer].add_object(
                                ag.RotationSurface(p1, p2, ag.Spline(plane, *points)), random_color)
                            self.full_update()
                            return True
                        points.append(ag.Point(self.pm.convert_screen_x_to_ag_x(res[0]),
                                               self.pm.convert_screen_y_to_ag_y(res[1]),
                                               plane.z(self.pm.convert_screen_x_to_ag_x(res[0]),
                                                       self.pm.convert_screen_y_to_ag_y(res[1]))))
                if self.point_is_on_plot(pos):
                    pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                    if len(points) == 1:
                        GeneralObject(self, ag.Segment(points[0], ag.Point(
                            self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                            plane.z(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                    self.pm.convert_screen_y_to_ag_y(pos[1])))), (0, 162, 232)).draw()
                    elif len(points) >= 2:
                        try:
                            GeneralObject(self, ag.Spline(plane, *points, ag.Point(
                            self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                            plane.z(self.pm.convert_screen_x_to_ag_x(pos[0]),
                                    self.pm.convert_screen_y_to_ag_y(pos[1])))), (0, 162, 232)).draw()
                        except Exception:
                            pass
                    s1.draw()
                    s2.draw()
                    l1.draw()
                    l2.draw()
                    self.screen.update()
                    self.clock.tick(30)

    def create_sphere(self):
        if (r := self.select_screen_point('xy')) is not None:
            x, y = r
        else:
            return
        a1 = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point('xz', x=x, y=y, objects=(a1,))) is not None:
            z = r
        else:
            return
        a2 = ScreenPoint(self, x, z, (0, 162, 232))
        center = ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                          self.pm.convert_screen_y_to_ag_z(z))
        if (r := self.select_screen_point('xy', objects=(a1, a2), func=lambda pos: GeneralObject(
                self, ag.Sphere(center, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(pos[0]), self.pm.convert_screen_y_to_ag_y(pos[1]),
                    center.z),
                    center)), (0, 162, 232)).draw())) is not None:
            x0, y0 = r
        else:
            return
        self.layers[self.current_layer].add_object(ag.Sphere(center, ag.distance(ag.Point(
                    self.pm.convert_screen_x_to_ag_x(x0), self.pm.convert_screen_y_to_ag_y(y0),
                    center.z),
                    center)), Plot.random_color())
        self.full_update()
        return True
