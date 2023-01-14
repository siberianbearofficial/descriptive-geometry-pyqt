import pygame as pg
import utils.maths.angem as ag
from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager
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

        self.layers = [Layer(self)]

        self.axis = Axis(self)
        self.pm = ProjectionManager(self)

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
        self.screen.full_update_toolbars()

    def zoom_out(self):
        self.zoom /= 2
        self.pm.zoom /= 2
        for layer in self.layers:
            layer.update_projections()
        self.full_update()
        self.screen.full_update_toolbars()

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

    def select_screen_point(self, x_y=None, segment=None, objects=tuple(), last_point=None):
        clock = pg.time.Clock()
        while True:
            self.full_update()
            pos = self.layers[0].snap_get_pos(self.screen, pg.mouse.get_pos(), x_y, last_point)
            events = pg.event.get()
            for event in events:
                if Plot.check_exit_event(event):
                    return None
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.point_is_on_plot(event.pos):
                    res = self.layers[0].snap_get_pos(self.screen, pg.mouse.get_pos(), x_y, last_point)
                    if x_y is None:
                        return res
                    else:
                        return res[1]
            if self.point_is_on_plot(pos):
                if x_y is None:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                    if segment is not None:
                        pg.draw.line(self.screen.screen, (0, 162, 232), segment, pos, 2)
                else:
                    pg.draw.circle(self.screen.screen, (0, 162, 232), pos, 3)
                    pg.draw.line(self.screen.screen, (180, 180, 180), x_y, pos, 2)
                    if segment is not None:
                        pg.draw.line(self.screen.screen, (0, 162, 232), segment, pos, 2)
                for obj in objects:
                    obj.draw()
                self.screen.update()
                clock.tick(30)

    def create_point(self):
        if (r := self.select_screen_point()) is not None:
            x, y = r
        else:
            return
        a = ScreenPoint(self, x, y, (0, 162, 232))
        if (r := self.select_screen_point((x, y), objects=(a,))) is not None:
            z = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[0].add_object(ag.Point(self.pm.convert_screen_x_to_ag_x(x), self.pm.convert_screen_y_to_ag_y(y),
                                           self.pm.convert_screen_y_to_ag_z(z)), random_color)
        self.full_update()
        return True

    def create_segment(self):
        if (r := self.select_screen_point()) is not None:
            x1, y1 = r
        else:
            return
        a1 = ScreenPoint(self, x1, y1, (0, 162, 232))
        if (r := self.select_screen_point(segment=(x1, y1), objects=(a1,), last_point=(x1, y1))) is not None:
            x2, y2 = r
        else:
            return
        a2 = ScreenPoint(self, x2, y2, (0, 162, 232))
        s1 = ScreenSegment(self, a1, a2, (0, 162, 232))
        if (r := self.select_screen_point((x1, y1), objects=(a1, a2, s1))) is not None:
            z1 = r
        else:
            return
        b1 = ScreenPoint(self, x1, z1, (0, 162, 232))
        s2 = ScreenSegment(self, a1, b1, (180, 180, 180))
        if (r := self.select_screen_point((x2, y2), segment=(x1, z1), objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[0].add_object(ag.Segment(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), random_color)
        self.full_update()
        return True

    def create_line(self):
        if (r := self.select_screen_point()) is not None:
            x1, y1 = r
        else:
            return
        a1 = ScreenPoint(self, x1, y1, (0, 162, 232))
        if (r := self.select_screen_point(segment=(x1, y1), objects=(a1,))) is not None:
            x2, y2 = r
        else:
            return
        a2 = ScreenPoint(self, x2, y2, (0, 162, 232))
        s1 = ScreenSegment(self, a1, a2, (0, 162, 232))
        if (r := self.select_screen_point((x1, y1), objects=(a1, a2, s1))) is not None:
            z1 = r
        else:
            return
        b1 = ScreenPoint(self, x1, z1, (0, 162, 232))
        s2 = ScreenSegment(self, a1, b1, (180, 180, 180))
        if (r := self.select_screen_point((x2, y2), segment=(x1, z1), objects=(a1, a2, s1, b1, s2))) is not None:
            z2 = r
        else:
            return
        random_color = (random.randint(50, 180), random.randint(80, 180), random.randint(50, 180))
        self.layers[0].add_object(ag.Line(
            ag.Point(self.pm.convert_screen_x_to_ag_x(x1), self.pm.convert_screen_y_to_ag_y(y1),
                     self.pm.convert_screen_y_to_ag_z(z1)),
            ag.Point(self.pm.convert_screen_x_to_ag_x(x2), self.pm.convert_screen_y_to_ag_y(y2),
                     self.pm.convert_screen_y_to_ag_z(z2))), random_color)
        self.full_update()
        return True
