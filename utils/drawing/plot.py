import pygame as pg
import utils.maths.angem as ag
from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager


class Plot:

    POINT_SELECTION = 0
    SEGMENT_SELECTION = 1

    def __init__(self, screen):
        self.screen = screen
        self.click_listening = False
        self.action = None

        # TODO: The plot may not have the same dimensions as the screen so that the screen can be scaled
        self.tlp = screen.tlp
        self.brp = screen.brp

        self.bg_color = (255, 255, 255)

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
