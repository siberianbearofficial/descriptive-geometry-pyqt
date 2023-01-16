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

    def get_snap(self, screen, pos, plane, x=None, y=None, z=None, last_point=None):
        self.x, self.y, self.z = x, y, z
        self.plane = plane
        self.last_point = last_point
        if plane == 'xy':
            p = (pos[0] if x is None else x, pos[1] if y is None else y)
            for el in self.snaps:
                for snap in el.func(self, p):
                    if x is not None and abs(x - snap[0]) < 1 and abs(pos[1] - snap[1]) <= 10:
                        el.draw(screen, snap)
                        return snap
                    if y is not None and abs(y - snap[1]) < 1 and abs(pos[0] - snap[0]) <= 10:
                        el.draw(screen, snap)
                        return snap
                    if x is None and y is None and distance(pos, snap) <= 10:
                        el.draw(screen, snap)
                        return snap
            return p
        if plane == 'xz':
            p = (pos[0] if x is None else x, pos[1] if z is None else z)
            for el in self.snaps:
                for snap in el.func(self, p):
                    if x is not None and abs(x - snap[0]) < 1 and abs(pos[1] - snap[1]) <= 10:
                        el.draw(screen, snap)
                        return snap
                    if z is not None and abs(z - snap[1]) < 1 and abs(pos[0] - snap[0]) <= 10:
                        el.draw(screen, snap)
                        return snap
                    if x is None and z is None and distance(pos, snap) <= 10:
                        el.draw(screen, snap)
                        return snap
            return p
        return pos

    def get_screen_objects(self, plane):
        for layer in self.plot.layers:
            if layer.hidden:
                continue
            for obj in layer.objects:
                for el in obj.xy_projection if plane == 'xy' else obj.xz_projection:
                    yield el

    def snap_point(self, pos):
        for obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenPoint):
                yield obj.tuple()

    def snap_segment_points(self, pos):
        for obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenSegment):
                yield obj.p1.tuple()
                yield obj.p2.tuple()

    def snap_nearest_point(self, pos):
        if self.plane == 'xy':
            for obj in self.get_screen_objects(self.plane):
                if isinstance(obj, ScreenSegment):
                    yield nearest_point(pos, obj)
        else:
            for obj in self.get_screen_objects(self.plane):
                if isinstance(obj, ScreenSegment):
                    if min(obj.p1.x, obj.p2.x) < pos[0] < max(obj.p1.x, obj.p2.x):
                        k = ((obj.p1.y - obj.p2.y) / (obj.p1.x - obj.p2.x)) if obj.p1.x - obj.p2.x != 0 else 10000000000
                        b = obj.p1.y - obj.p1.x * k
                        yield pos[0], k * pos[0] + b

    def snap_perpendicular(self, pos):
        if self.last_point is not None and self.plane == 'xy':
            for obj in self.get_screen_objects(self.plane):
                if isinstance(obj, ScreenSegment):
                    yield nearest_point(self.last_point, obj)


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
    if segment.p1.x - segment.p2.x == 0:
        k1 = 100000000000
    else:
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