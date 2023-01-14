import pygame as pg
import utils.maths.angem as ag
from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager
from utils.drawing.layer import Layer
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

    def clear(self):
        pg.draw.rect(self.screen.screen, self.bg_color,
                     (self.tlp[0], self.tlp[1], self.brp[0], self.brp[1]))
        self.axis.draw()
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

    def full_update(self):
        pg.draw.rect(self.screen.screen, self.bg_color,
                     (self.tlp[0], self.tlp[1] - 2, self.brp[0] - self.tlp[0], self.brp[1] - self.tlp[1] + 4))
        self.axis.draw()
        for layer in self.layers:
            layer.draw()

    def point_is_on_plot(self, point):
        return self.tlp[0] < point[0] < self.brp[0] and self.tlp[1] < point[1] < self.brp[1]

    def create_point(self):
        clock = pg.time.Clock()
        while True:
            self.full_update()
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        return False
                    elif event.button == 1 and self.point_is_on_plot(event.pos):
                        x, y = event.pos
                        while True:
                            self.full_update()
                            events = pg.event.get()
                            for event in events:
                                if event.type == pg.QUIT:
                                    pg.quit()
                                    exit(0)
                                elif event.type == pg.MOUSEBUTTONDOWN:
                                    if event.button == 3:
                                        return False
                                    elif event.button == 1 and self.point_is_on_plot(event.pos):
                                        z = event.pos[1]
                                        random_color = (random.randint(50, 180),
                                                        random.randint(80, 180), random.randint(50, 180))
                                        self.layers[0].add_object(ag.Point(self.pm.convert_screen_x_to_ag_x(x),
                                                                  self.pm.convert_screen_y_to_ag_y(y),
                                                                  self.pm.convert_screen_y_to_ag_z(z)), random_color)
                                        self.full_update()
                                        return True
                            if self.point_is_on_plot(pg.mouse.get_pos()):
                                pg.draw.circle(self.screen.screen, (0, 162, 232), (x, y), 3)
                                pg.draw.circle(self.screen.screen, (0, 162, 232), (x, z := pg.mouse.get_pos()[1]), 3)
                                pg.draw.line(self.screen.screen, (180, 180, 180), (x, y), (x, z))
                                self.screen.update()
                                clock.tick(30)

            if self.point_is_on_plot(pg.mouse.get_pos()):
                pg.draw.circle(self.screen.screen, (0, 162, 232), pg.mouse.get_pos(), 3)
                self.screen.update()
                clock.tick(30)

    def create_segment(self):
        def second_point():
            while True:
                self.full_update()
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit()
                        exit(0)
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            return False
                        elif event.button == 1 and self.point_is_on_plot(event.pos):
                            z1 = event.pos[1]
                            while True:
                                self.full_update()
                                events = pg.event.get()
                                for event in events:
                                    if event.type == pg.QUIT:
                                        pg.quit()
                                        exit(0)
                                    elif event.type == pg.MOUSEBUTTONDOWN:
                                        if event.button == 3:
                                            return False
                                        elif event.button == 1 and self.point_is_on_plot(event.pos):
                                            z2 = event.pos[1]
                                            random_color = (random.randint(50, 180),
                                                            random.randint(80, 180), random.randint(50, 180))
                                            self.layers[0].add_object(ag.Segment(
                                                ag.Point(self.pm.convert_screen_x_to_ag_x(x1),
                                                         self.pm.convert_screen_y_to_ag_y(y1),
                                                         self.pm.convert_screen_y_to_ag_z(z1)),
                                                ag.Point(self.pm.convert_screen_x_to_ag_x(x2),
                                                         self.pm.convert_screen_y_to_ag_y(y2),
                                                         self.pm.convert_screen_y_to_ag_z(z2))),
                                                          random_color)
                                            self.full_update()
                                            return True
                                if self.point_is_on_plot(pg.mouse.get_pos()):
                                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x1, y1), 3)
                                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x2, y2), 3)
                                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x1, z1), 3)
                                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x2, z2 := pg.mouse.get_pos()[1]),
                                                   3)
                                    pg.draw.line(self.screen.screen, (0, 162, 232), (x1, y1), (x2, y2))
                                    pg.draw.line(self.screen.screen, (0, 162, 232), (x1, z1), (x2, z2))
                                    pg.draw.line(self.screen.screen, (180, 180, 180), (x1, y1), (x1, z1))
                                    pg.draw.line(self.screen.screen, (180, 180, 180), (x2, y2), (x2, z2))
                                    self.screen.update()
                                    clock.tick(30)
                if self.point_is_on_plot(pg.mouse.get_pos()):
                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x1, y1), 3)
                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x2, y2), 3)
                    pg.draw.circle(self.screen.screen, (0, 162, 232), (x1, z1 := pg.mouse.get_pos()[1]), 3)
                    pg.draw.line(self.screen.screen, (0, 162, 232), (x1, y1), (x2, y2))
                    pg.draw.line(self.screen.screen, (180, 180, 180), (x1, y1), (x1, z1))
                    self.screen.update()
                    clock.tick(30)

        clock = pg.time.Clock()
        while True:
            self.full_update()
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        return False
                    elif event.button == 1 and self.point_is_on_plot(event.pos):
                        x1, y1 = event.pos
                        while True:
                            self.full_update()
                            events = pg.event.get()
                            for event in events:
                                if event.type == pg.QUIT:
                                    pg.quit()
                                    exit(0)
                                elif event.type == pg.MOUSEBUTTONDOWN:
                                    if event.button == 3:
                                        return False
                                    elif event.button == 1 and self.point_is_on_plot(event.pos):
                                        x2, y2 = event.pos
                                        second_point()
                                        return
                            if self.point_is_on_plot(pg.mouse.get_pos()):
                                pg.draw.circle(self.screen.screen, (0, 162, 232), (x1, y1), 3)
                                pg.draw.circle(self.screen.screen, (0, 162, 232), pg.mouse.get_pos(), 3)
                                pg.draw.line(self.screen.screen, (0, 162, 232), (x1, y1), pg.mouse.get_pos())
                                self.screen.update()
                                clock.tick(30)

            if self.point_is_on_plot(pg.mouse.get_pos()):
                pg.draw.circle(self.screen.screen, (0, 162, 232), pg.mouse.get_pos(), 3)
                self.screen.update()
                clock.tick(30)
