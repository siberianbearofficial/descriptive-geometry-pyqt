from PyQt6.QtCore import QPointF

from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
import core.angem as ag


class SnapManager:
    def __init__(self, object_manager):
        self.om = object_manager
        self.snaps = [
            Snap(SnapManager.snap_point, 'point'),
            # Snap(SnapManager.snap_segment_points, 'point'),
            # Snap(SnapManager.snap_intersection, 'intersection'),
            Snap(SnapManager.snap_nearest_point, 'nearest'),
            # Snap(SnapManager.snap_nearest_point_2, 'nearest')
        ]

        self.intersections_xy = []
        self.intersections_xz = []
        self.x, self.c = 0, 0
        self.x_fix, self.c_fix = False, False
        self.pos = QPointF(0, 0)
        self.plane = 'xy'
        self.scale = 1

    def get_snap(self, pos, plane, x=None, c=None, scale=1, snap_type=False):
        self.x, self.c = x if x is not None else pos.x(), c if c is not None else pos.y()
        self.x_fix, self.c_fix = x is not None, c is not None
        self.pos = pos
        self.plane = plane
        self.scale = scale
        for snap in self.snaps:
            if p := snap.func(self):
                return p
        return pos

    def get_screen_objects(self, plane):
        for obj in self.om.get_all_objects():
            for el in obj.xy_projections if plane == 'xy' else obj.xz_projections:
                yield el, obj

    def snap_point(self):
        pos = ScreenPoint(self.x, self.c)
        res = None
        min_dist = 10 / self.scale
        for obj, ag_obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenPoint) and (dist := obj.distance(pos)) <= min_dist:
                res = QPointF(*obj)
                min_dist = dist
        return res

    def snap_segment_points(self):
        for obj, ag_obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenSegment):
                yield obj.p1, ag_obj
                yield obj.p2, ag_obj

    def snap_intersection(self, pos):
        if self.plane == 'xy':
            for el in self.intersections_xy:
                yield el, None
        elif self.plane == 'xz':
            for el in self.intersections_xz:
                yield el, None

    def snap_nearest_point(self):
        pos = ScreenPoint(self.x, self.c)
        res = None
        min_dist = 10 / self.scale
        for obj, ag_obj in self.get_screen_objects(self.plane):
            try:
                if isinstance(obj, ScreenSegment):
                    if self.x_fix:
                        if not min(obj.p1.x, obj.p2.x) <= self.x <= max(obj.p1.x, obj.p2.x):
                            continue
                        dist = pos.distance(point := ScreenPoint(self.x, obj.y(self.x)))
                    elif self.c_fix:
                        if not min(obj.p1.y, obj.p2.y) <= self.c <= max(obj.p1.y, obj.p2.y):
                            continue
                        dist = pos.distance(point := ScreenPoint(obj.x(self.c), self.c))
                    else:
                        dist = pos.distance(point := obj.nearest(pos, as_line=False))
                    if dist <= min_dist:
                        res = QPointF(*point)
                        min_dist = dist
            except ZeroDivisionError:
                pass
        return res

    def snap_nearest_point_2(self, pos):
        point, dist, ag_obj_res = pos, 10000, None
        for obj, ag_obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ThinScreenPoint) and (d := distance(pos, obj.tuple())) < dist and (
                    self.x is None or (obj.x - self.x) <= 1):
                point = obj.tuple()
                dist = d
                ag_obj_res = ag_obj
        yield point, ag_obj_res

    def update_intersections(self):
        lst = []
        self.intersections_xy.clear()
        for obj1, _ in self.get_screen_objects('xy'):
            if isinstance(obj1, ScreenSegment):
                if obj1.p1[0] - obj1.p2[0] == 0:
                    k = 100000000000
                else:
                    k = (obj1.p1[1] - obj1.p2[1]) / (obj1.p1[0] - obj1.p2[0])
                b = obj1.p1[1] - obj1.p1[0] * k
                for obj2 in lst:
                    if k == obj2[1]:
                        continue
                    x = (obj2[2] - b) / (k - obj2[1])
                    y = k * x + b
                    if min(obj1.p1[0], obj1.p2[0]) <= x <= max(obj1.p1[0], obj1.p2[0]) and \
                            min(obj2[0].p1[0], obj2[0].p2[0]) <= x <= max(obj2[0].p1[0], obj2[0].p2[0]):
                        self.intersections_xy.append((x, y))
                lst.append((obj1, k, b))
        lst.clear()
        self.intersections_xz.clear()
        for obj1, _ in self.get_screen_objects('xz'):
            if isinstance(obj1, ScreenSegment):
                if obj1.p1[0] - obj1.p2[0] == 0:
                    k = 100000000000
                else:
                    k = (obj1.p1[1] - obj1.p2[1]) / (obj1.p1[0] - obj1.p2[0])
                b = obj1.p1[1] - obj1.p1[0] * k
                for obj2 in lst:
                    if k == obj2[1]:
                        continue
                    x = (obj2[2] - b) / (k - obj2[1])
                    y = k * x + b
                    if min(obj1.p1[0], obj1.p2[0]) <= x <= max(obj1.p1[0], obj1.p2[0]) and \
                            min(obj2[0].p1[0], obj2[0].p2[0]) <= x <= max(obj2[0].p1[0], obj2[0].p2[0]):
                        self.intersections_xz.append((x, y))
                lst.append((obj1, k, b))


class Snap:
    def __init__(self, func, image):
        self.func = func
        self.name = image

    def __str__(self):
        return 'Snap ' + self.name
