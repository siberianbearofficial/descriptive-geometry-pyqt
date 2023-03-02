from PyQt5.QtWidgets import QLabel
import utils.maths.angem as ag
from utils.drawing.screen_point import ScreenPoint

SEP = '-'
DIST1 = 5
DIST2 = 10


class ObjectNameBar(QLabel):
    def __init__(self, parent, pos, bottom=False, text=''):
        super(ObjectNameBar, self).__init__(parent)
        self.plot = parent
        if pos is None:
            self.hide()
        else:
            if bottom:
                self.setGeometry(pos[0] + 10, pos[1] - 16, 50, 16)
            else:
                self.setGeometry(pos[0] + 10, pos[1], 50, 16)
            self.show()
        self.setText(text)
        self.setStyleSheet(f"background-color: rgb({parent.bg_color})")

    def move2(self, x, y):
        self.move(self.x() + x, self.y() + y)

    def move3(self, x, y, bottom=False):
        if bottom:
            self.move(x + 10, y - 16)
        else:
            self.move(x + 10, y)


def get_name_bar_text(obj):
    if isinstance(obj.ag_object, ag.Point):
        return obj.name + "'", obj.name + "''"
    if isinstance(obj.ag_object, ag.Segment):
        if obj.name.count(SEP) == 1:
            name = obj.name.split(SEP)
            return name[0] + "'", name[1] + "'", name[0] + "''", name[1] + "''"
        return obj.name + "'", obj.name + "''"
    if isinstance(obj.ag_object, ag.Line) or isinstance(obj.ag_object, ag.Plane):
        return obj.name + "'", obj.name + "''"
    return tuple()


def get_name_bar_pos(obj):
    if isinstance(obj.ag_object, ag.Point):
        return (obj.xy_projection[0].tuple(), True), (obj.xz_projection[0].tuple(), True)

    if isinstance(obj.ag_object, ag.Segment):
        # TODO: Предусмотреть изменение имени
        if obj.name.count(SEP) == 1:
            if obj.xy_projection[0].k is None:
                return (tuple(obj.xy_projection[0].p1), True), (tuple(obj.xy_projection[0].p2), False), \
                       (tuple(obj.xz_projection[0].p1), True), (tuple(obj.xz_projection[0].p2), True)
            if obj.xz_projection[0].k is None:
                return (tuple(obj.xy_projection[0].p1), True), (tuple(obj.xy_projection[0].p2), True), \
                       (tuple(obj.xz_projection[0].p1), True), (tuple(obj.xz_projection[0].p2), False)
            return (get_point(obj.xy_projection[0].p1, obj.xy_projection[0].k, DIST1, True, True),
                    obj.xy_projection[0].k > 0), \
                   (get_point(obj.xy_projection[0].p2, obj.xy_projection[0].k, DIST1, True, True),
                    obj.xy_projection[0].k > 0), \
                   (get_point(obj.xz_projection[0].p1, obj.xz_projection[0].k, DIST1, True, True),
                    obj.xz_projection[0].k > 0), \
                   (get_point(obj.xz_projection[0].p2, obj.xz_projection[0].k, DIST1, True, True),
                    obj.xz_projection[0].k > 0)
        else:
            return (get_point(((obj.xy_projection[0].p1[0] + obj.xy_projection[0].p2[0]) / 2,
                               (obj.xy_projection[0].p1[1] + obj.xy_projection[0].p2[1]) / 2),
                              obj.xy_projection[0].k, DIST1, True, True), True), \
                   (get_point(((obj.xz_projection[0].p1[0] + obj.xz_projection[0].p2[0]) / 2,
                               (obj.xz_projection[0].p1[1] + obj.xz_projection[0].p2[1]) / 2),
                              obj.xz_projection[0].k, DIST1, True, True), True)

    if isinstance(obj.ag_object, ag.Line) or isinstance(obj.ag_object, ag.Plane):
        if isinstance(obj.xy_projection[0], ScreenPoint):
            res_p1 = (obj.xy_projection[0].tuple(), True)
        else:
            if obj.xy_projection[0].p1[1] > obj.xy_projection[0].p2[1]:
                p1 = obj.xy_projection[0].p1
                p1_by_y = obj.xy_projection[0].p1_by_y
            else:
                p1 = obj.xy_projection[0].p2
                p1_by_y = obj.xy_projection[0].p2_by_y
            if not obj.xy_projection[0].drawing:
                res_p1 = None
            elif obj.xy_projection[0].k is None:
                res_p1 = (get_point((obj.xy_projection[0].p1[0], obj.plot.brp[1] - 10),
                                    obj.xy_projection[0].k, DIST1, True, True), True)
            elif p1_by_y:
                x = obj.plot.brp[0] - 50 if obj.xy_projection[0].k > 0 else obj.plot.tlp[0] + 5
                res_p1 = (get_point((x, obj.xy_projection[0].y(x)),
                                    obj.xy_projection[0].k, DIST1, True, True), obj.xy_projection[0].k > 0)
            else:
                d = 10 if obj.xy_projection[0].k > 0 else 30
                res_p1 = (get_point((obj.xy_projection[0].x(p1[1] - d), p1[1] - d),
                                    obj.xy_projection[0].k, DIST1, True, True), obj.xy_projection[0].k > 0)

        if isinstance(obj.xz_projection[0], ScreenPoint):
            res_p2 = (obj.xz_projection[0].tuple(), True)
        else:
            if obj.xz_projection[0].p1[1] < obj.xz_projection[0].p2[1]:
                p2 = obj.xz_projection[0].p1
                p2_by_y = obj.xz_projection[0].p1_by_y
            else:
                p2 = obj.xz_projection[0].p2
                p2_by_y = obj.xz_projection[0].p2_by_y
            if not obj.xz_projection[0].drawing:
                res_p2 = None
            elif obj.xz_projection[0].k is None:
                res_p2 = (get_point((obj.xz_projection[0].p1[0], obj.plot.tlp[1] + 10),
                                    obj.xz_projection[0].k, DIST1, True, True), False)
            elif p2_by_y:
                x = obj.plot.tlp[0] + 5 if obj.xz_projection[0].k > 0 else obj.plot.brp[0] - 50
                res_p2 = (get_point((x, obj.xz_projection[0].y(x)),
                                    obj.xz_projection[0].k, DIST1, True, True), obj.xz_projection[0].k > 0)
            else:
                d = 30 if obj.xz_projection[0].k > 0 else 10
                res_p2 = (get_point((obj.xz_projection[0].x(p2[1] + d), p2[1] + d),
                                    obj.xz_projection[0].k, DIST1, True, True), obj.xz_projection[0].k > 0)

        return res_p1, res_p2

    return tuple()


def get_point(point, k, dist, right, perpendicular=False):
    if perpendicular:
        if k:
            k = -1 / k
        elif k is None:
            k = 0
        else:
            k = None
    if k is None:
        c = 0
        s = 1
    else:
        c = (1 / (1 + k ** 2)) ** 0.5
        s = (1 - c ** 2) ** 0.5
        if k < 0:
            if right:
                s *= -1
            else:
                c *= -1
    return int(point[0] + dist * c), int(point[1] + dist * s)
