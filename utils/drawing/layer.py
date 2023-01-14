from utils.drawing.general_object import GeneralObject
import pygame as pg

from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment


class Layer:
    def __init__(self, plot, hidden=False):
        self.plot = plot
        self.hidden = hidden
        self.objects = []
        self.snaps = [Snap(Layer.snap_point, 'point'),
                      Snap(Layer.snap_segment_points, 'point'),
                      Snap(Layer.snap_perpendicular, 'perpendicular'),
                      Snap(Layer.snap_nearest_point, 'nearest')]

    def add_object(self, ag_object, color):
        self.objects.append(GeneralObject(self.plot, ag_object, color))

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        self.objects = []

    def snap_get_pos(self, screen, pos, x_y=None, last_point=None):
        if x_y is not None:
            for el in self.snaps:
                for snap in el.func(self, (x_y[0], pos[1]),  'xz', last_point):
                    if abs(x_y[0] - snap[0]) < 1 and abs(pos[1] - snap[1]) <= 10:
                        el.draw(screen, snap)
                        return snap
            return x_y[0], pos[1]
        for el in self.snaps:
            for snap in el.func(self, pos, 'xy', last_point):
                if distance(pos, snap) <= 10:
                    el.draw(screen, snap)
                    return snap
        return pos

    def snap_point(self, pos, plane, last_point):
        for obj in self.objects:
            if plane == 'xy':
                for el in obj.xy_projection:
                    if isinstance(el, ScreenPoint):
                        yield el.tuple()
            if plane == 'xz':
                for el in obj.xz_projection:
                    if isinstance(el, ScreenPoint):
                        yield el.tuple()

    def snap_segment_points(self, pos, plane, last_point):
        for obj in self.objects:
            if plane == 'xy':
                for el in obj.xy_projection:
                    if isinstance(el, ScreenSegment):
                        yield el.p1.tuple()
                        yield el.p2.tuple()
            if plane == 'xz':
                for el in obj.xz_projection:
                    if isinstance(el, ScreenSegment):
                        yield el.p1.tuple()
                        yield el.p2.tuple()

    def snap_nearest_point(self, pos, plane, last_point):
        for obj in self.objects:
            if plane == 'xy':
                for el in obj.xy_projection:
                    if isinstance(el, ScreenSegment):
                        yield nearest_point(pos, el)
            if plane == 'xz':
                for el in obj.xz_projection:
                    if isinstance(el, ScreenSegment):
                        if min(el.p1.x, el.p2.x) < pos[0] < max(el.p1.x, el.p2.x):
                            k = (el.p1.y - el.p2.y) / (el.p1.x - el.p2.x)
                            b = el.p1.y - el.p1.x * k
                            yield pos[0], k * pos[0] + b

    def snap_perpendicular(self, pos, plane, last_point):
        if last_point is not None:
            for obj in self.objects:
                if plane == 'xy':
                    for el in obj.xy_projection:
                        if isinstance(el, ScreenSegment):
                            yield nearest_point(last_point, el)


class Snap:
    def __init__(self, func, image):
        self.func = func
        self.image = pg.image.load('images\\snap_' + image + '.bmp')
        self.image.set_colorkey((255, 255, 255))

    def draw(self, screen, pos):
        screen.screen.blit(self.image, (pos[0] - 8, pos[1] - 8))


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def nearest_point(point, segment):
    k1 = (segment.p1.y - segment.p2.y) / (segment.p1.x - segment.p2.x)
    b1 = segment.p1.y - segment.p1.x * k1
    k2 = -1 / k1
    b2 = point[1] - point[0] * k2
    intersection_point = (b2 - b1) / (k1 - k2)
    intersection_point = intersection_point, k1 * intersection_point + b1
    if min(segment.p1.x, segment.p2.x) < intersection_point[0] < max(segment.p1.x, segment.p2.x):
        return intersection_point
    elif distance(point, segment.p1.tuple()) < distance(point, segment.p2.tuple()):
        return segment.p1.tuple()
    return segment.p2.tuple()