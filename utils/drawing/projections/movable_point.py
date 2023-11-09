from PyQt6.QtCore import QPoint

from utils.drawing.projections.screen_point import ScreenPoint
from utils.drawing.snap import SnapManager
from utils.objects.general_object import GeneralObject
import utils.drawing.projections.projection_manager as projections
import core.angem as ag


class ObjectMoveManager:
    def __init__(self, canvass, obj: GeneralObject):
        self.canvass = canvass
        self.object_manager = canvass.object_manager
        self.object = obj
        self.snap_manager = SnapManager(self.object_manager)
        self.object_dict = obj.to_dict()['ag_object']
        self.points = []
        self.update_points()

        self.moving_point = None
        self.last_pos = None

    def mouse_left(self, pos: QPoint, scale=1):
        for i, point in enumerate(self.points):
            if ScreenPoint(pos.x(), pos.y()).distance(point.point) < 10 / scale:
                self.moving_point = point
                self.last_pos = pos
                return True
        return False

    def mouse_left_release(self):
        if self.moving_point is not None:
            self.moving_point = None
            self.last_pos = None
            return True
        return False

    def mouse_move(self, pos: QPoint):
        if self.moving_point is None:
            return False
        pos = self.snap_manager.get_snap(pos, self.moving_point.plane, scale=self.canvass.scale)
        self.moving_point.move(pos.x(), pos.y())
        for point in self.points:
            if point == self.moving_point:
                continue
            point.update()
        self.object_manager.set_object_ag_obj(self.object_dict)
        return True

    def update_points(self):
        self.points.clear()
        match self.object.ag_object.__class__:
            case ag.Point:
                self.points = [MovablePoint(self.canvass, self.object_dict, 'x', 'y'),
                               MovablePoint(self.canvass, self.object_dict, 'x', 'z', plane='xz')]
            case ag.Segment:
                self.points = [MovablePoint(self.canvass, self.object_dict, 'p1/x', 'p1/y'),
                               MovablePoint(self.canvass, self.object_dict, 'p1/x', 'p1/z', plane='xz'),
                               MovablePoint(self.canvass, self.object_dict, 'p2/x', 'p2/y'),
                               MovablePoint(self.canvass, self.object_dict, 'p2/x', 'p2/z', plane='xz')]
            case ag.Cylinder:
                self.points = [MovablePoint(self.canvass, self.object_dict, 'center1/x', 'center1/y'),
                               MovablePoint(self.canvass, self.object_dict, 'center1/x', 'center1/z', plane='xz'),
                               MovablePoint(self.canvass, self.object_dict, 'center2/x', 'center2/y'),
                               MovablePoint(self.canvass, self.object_dict, 'center2/x', 'center2/z', plane='xz')]
            case ag.Cone:
                self.points = [MovablePoint(self.canvass, self.object_dict, 'center1/x', 'center1/y'),
                               MovablePoint(self.canvass, self.object_dict, 'center1/x', 'center1/z', plane='xz'),
                               MovablePoint(self.canvass, self.object_dict, 'center2/x', 'center2/y'),
                               MovablePoint(self.canvass, self.object_dict, 'center2/x', 'center2/z', plane='xz')]


class MovablePoint:
    def __init__(self, canvass, obj_dict: dict, x_key, y_key, plane='xy'):
        self.dict = obj_dict
        self.canvass = canvass
        self.x_key = x_key
        self.y_key = y_key
        self.plane = plane
        self.point = None
        self.update()

    def update(self):
        if self.plane == 'xy':
            self.point = ScreenPoint(projections.ag_x_to_screen_x(self._get(self.x_key)),
                                     projections.ag_y_to_screen_y(self._get(self.y_key)),
                                     color=self.canvass.draw_color, thickness=6)
        else:
            self.point = ScreenPoint(projections.ag_x_to_screen_x(self._get(self.x_key)),
                                     projections.ag_z_to_screen_y(self._get(self.y_key)),
                                     color=self.canvass.draw_color, thickness=6)

    def move(self, x, y):
        self.point.x = x
        self.point.y = y
        self._set(self.x_key, projections.screen_x_to_ag_x(x))
        if self.plane == 'xy':
            self._set(self.y_key, projections.screen_y_to_ag_y(y))
        else:
            self._set(self.y_key, projections.screen_y_to_ag_z(y))

    def _get(self, key):
        dct = self.dict
        key = key.split('/')
        for i in range(len(key) - 1):
            dct = dct[key[i]]
        return dct[key[-1]]

    def _set(self, key, value):
        dct = self.dict
        key = key.split('/')
        for i in range(len(key) - 1):
            dct = dct[key[i]]
        dct[key[-1]] = value
