import pygame as pg

from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment


class SnapManager:
    def __init__(self, plot):
        self.plot = plot
        self.snaps = [Snap(SnapManager.snap_point, 'point'),
                      Snap(SnapManager.snap_segment_points, 'point'),
                      Snap(SnapManager.snap_perpendicular, 'perpendicular'),
                      Snap(SnapManager.snap_nearest_point, 'nearest')]

    def get_snap(self, screen, pos, x_y=None, last_point=None):
        if x_y is not None:
            for el in self.snaps:
                for snap in el.func(self, (x_y[0], pos[1]), 'xz', last_point):
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

    def get_screen_objects(self, plane):
        for layer in self.plot.layers:
            for obj in layer.objects:
                for el in obj.xy_projection if plane == 'xy' else obj.xz_projection:
                    yield el

    def snap_point(self, pos, plane, last_point):
        for obj in self.get_screen_objects(plane):
            if isinstance(obj, ScreenPoint):
                yield obj.tuple()

    def snap_segment_points(self, pos, plane, last_point):
        for obj in self.get_screen_objects(plane):
            if isinstance(obj, ScreenSegment):
                yield obj.p1.tuple()
                yield obj.p2.tuple()

    def snap_nearest_point(self, pos, plane, last_point):
        if plane == 'xy':
            for obj in self.get_screen_objects(plane):
                if isinstance(obj, ScreenSegment):
                    yield nearest_point(pos, obj)
        else:
            for obj in self.get_screen_objects(plane):
                if isinstance(obj, ScreenSegment):
                    if min(obj.p1.x, obj.p2.x) < pos[0] < max(obj.p1.x, obj.p2.x):
                        k = (obj.p1.y - obj.p2.y) / (obj.p1.x - obj.p2.x)
                        b = obj.p1.y - obj.p1.x * k
                        yield pos[0], k * pos[0] + b

    def snap_perpendicular(self, pos, plane, last_point):
        if last_point is not None and plane == 'xy':
            for obj in self.get_screen_objects(plane):
                if isinstance(obj, ScreenSegment):
                    yield nearest_point(last_point, obj)


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
    if k1 != 0:
        k2 = -1 / k1
    else:
        k2 = 100000000000
    b2 = point[1] - point[0] * k2
    intersection_point = (b2 - b1) / (k1 - k2)
    intersection_point = intersection_point, k1 * intersection_point + b1
    if min(segment.p1.x, segment.p2.x) < intersection_point[0] < max(segment.p1.x, segment.p2.x):
        return intersection_point
    elif distance(point, segment.p1.tuple()) < distance(point, segment.p2.tuple()):
        return segment.p1.tuple()
    return segment.p2.tuple()