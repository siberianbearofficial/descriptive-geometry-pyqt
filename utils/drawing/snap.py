from PyQt6.QtCore import QPointF

from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
import core.angem as ag


class SnapManager:
    def __init__(self, object_manager):
        self.om = object_manager
        self.snaps = [
            Snap(SnapManager.snap_point, 'point'),
            Snap(SnapManager.snap_intersection, 'intersection'),
            Snap(SnapManager.snap_nearest_point, 'nearest'),
        ]

        self.intersections_xy = []
        self.intersections_xz = []
        self.x, self.c = 0, 0
        self.x_fix, self.c_fix = False, False
        self.pos = QPointF(0, 0)
        self.plane = 'xy'
        self.scale = 1
        self.update_intersections()

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
                yield el

    def snap_point(self):
        pos = ScreenPoint(self.x, self.c)
        res = None
        min_dist = 10 / self.scale
        for obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenPoint) and (dist := obj.distance(pos)) <= min_dist:
                res = QPointF(*obj)
                min_dist = dist
        return res

    def snap_intersection(self):
        pos = ScreenPoint(self.x, self.c)
        res = None
        min_dist = 10 / self.scale
        for obj in (self.intersections_xy if self.plane == 'xy' else self.intersections_xz):
            if (dist := obj.distance(pos)) <= min_dist:
                res = QPointF(*obj)
                min_dist = dist
        return res

    def snap_nearest_point(self):
        pos = ScreenPoint(self.x, self.c)
        res = None
        min_dist = 10 / self.scale
        for obj in self.get_screen_objects(self.plane):
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

    def update_intersections(self):
        self.intersections_xy.clear()
        for plane in ['xy', 'xz']:
            for obj1 in self.get_screen_objects(plane):
                for obj2 in self.get_screen_objects(plane):
                    if isinstance(obj1, ScreenSegment) and isinstance(obj2, ScreenSegment) and obj1 != obj2:
                        try:
                            point = obj1.intersection(obj2)
                            if point is not None:
                                if plane == 'xy':
                                    self.intersections_xy.append(point)
                                else:
                                    self.intersections_xz.append(point)
                        except Exception:
                            pass


class Snap:
    def __init__(self, func, image):
        self.func = func
        self.name = image

    def __str__(self):
        return 'Snap ' + self.name
