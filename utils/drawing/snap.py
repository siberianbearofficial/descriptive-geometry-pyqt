from utils.drawing.screen_point import ScreenPoint, ScreenPoint2
from utils.drawing.screen_segment import ScreenSegment
import utils.maths.angem as ag


class SnapManager:
    def __init__(self, plot):
        self.plot = plot
        self.snaps = [Snap(SnapManager.snap_point, 'point'),
                      Snap(SnapManager.snap_segment_points, 'point'),
                      Snap(SnapManager.snap_intersection, 'intersection'),
                      Snap(SnapManager.snap_nearest_point, 'nearest'),
                      Snap(SnapManager.snap_nearest_point_2, 'nearest')]

        self.intersections_xy = []
        self.intersections_xz = []
        self.x, self.y, self.z = 0, 0, 0
        self.plane = 'xy'

    def get_snap(self, pos, plane, x=None, y=None, z=None, snap_dist=10, snap_type=False):
        self.x, self.y, self.z = x, y, z
        self.plane = plane
        if plane == 'xy':
            p = (pos[0] if x is None else x, pos[1] if y is None else y)
            for el in self.snaps:
                for snap, obj in el.func(self, p):
                    if x is not None and abs(x - snap[0]) < 1 and abs(pos[1] - snap[1]) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
                    if y is not None and abs(y - snap[1]) < 1 and abs(pos[0] - snap[0]) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
                    if x is None and y is None and distance(pos, snap) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
            if snap_type:
                return p, None, None
            return p
        if plane == 'xz':
            p = (pos[0] if x is None else x, pos[1] if z is None else z)
            for el in self.snaps:
                for snap, obj in el.func(self, p):
                    if x is not None and abs(x - snap[0]) < 1 and abs(pos[1] - snap[1]) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
                    if z is not None and abs(z - snap[1]) < 1 and abs(pos[0] - snap[0]) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
                    if x is None and z is None and distance(pos, snap) <= snap_dist:
                        if snap_type:
                            return snap, el, obj
                        el.draw(snap)
                        return snap
            if snap_type:
                return p, None, None
            return p
        return pos

    def get_ag_snap(self, screen_x, screen_y, screen_z):
        snap_xy, snap_type_xy, obj_xy = self.get_snap((screen_x, screen_y), 'xy', snap_type=True, snap_dist=1)
        snap_xz, snap_type_xz, obj_xz = self.get_snap((screen_x, screen_z), 'xz', x=screen_x, y=screen_y,
                                                      snap_type=True, snap_dist=1)
        point = self.plot.pm.convert_screen_x_to_ag_x(snap_xy[0]), self.plot.pm.convert_screen_y_to_ag_y(snap_xy[1]), \
                self.plot.pm.convert_screen_y_to_ag_z(snap_xz[1])
        if snap_type_xy != snap_type_xz or obj_xy != obj_xz or snap_type_xy is None or snap_type_xy == self.snaps[4]:
            return point
        obj = obj_xy.ag_object
        if snap_type_xy == self.snaps[0]:
            if isinstance(obj, ag.Point):
                return obj.x, obj.y, obj.z
            if isinstance(obj, ag.Segment):
                p = obj.p1 if ag.distance(obj.p1, ag.Point(*point)) < ag.distance(obj.p2, ag.Point(*point)) else obj.p2
                return p.x, p.y, p.z
            if isinstance(obj, ag.Plane) and obj_xy.config.get('draw_3p', False):
                p = obj.point if ag.distance(obj.point, ag.Point(*point)) < ag.distance(
                    obj.point + obj.vector1, ag.Point(*point)) else obj.point + obj.vector1
                p = p if ag.distance(p, ag.Point(*point)) < ag.distance(
                    obj.point + obj.vector2, ag.Point(*point)) else obj.point + obj.vector2
                return p.x, p.y, p.z
        if snap_type_xy == self.snaps[3]:
            if isinstance(obj, ag.Line) or isinstance(obj, ag.Segment):
                line = obj if isinstance(obj, ag.Line) else ag.Line(obj.p1, obj.p2)
                n_point = ag.Line(ag.Point(*point), ag.Plane(ag.Point(*point), line).normal & line.vector)\
                    .intersection(line)
                return n_point.x, n_point.y, n_point.z
        return point

    def get_screen_objects(self, plane):
        for layer in self.plot.layers:
            if layer.hidden:
                continue
            for obj in layer.objects:
                for el in obj.xy_projection if plane == 'xy' else obj.xz_projection:
                    yield el, obj

    def snap_point(self, pos):
        for obj, ag_obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenPoint):
                yield obj.tuple(), ag_obj

    def snap_segment_points(self, pos):
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

    def snap_nearest_point(self, pos):
        if self.plane == 'xy':
            for obj, ag_obj in self.get_screen_objects(self.plane):
                if isinstance(obj, ScreenSegment):
                    yield nearest_point(pos, obj), ag_obj
        else:
            for obj, ag_obj in self.get_screen_objects(self.plane):
                if isinstance(obj, ScreenSegment):
                    if min(obj.p1[0], obj.p2[0]) < pos[0] < max(obj.p1[0], obj.p2[0]):
                        k = ((obj.p1[1] - obj.p2[1]) / (obj.p1[0] - obj.p2[0])) if obj.p1[0] - obj.p2[
                            0] != 0 else 10000000000
                        b = obj.p1[1] - obj.p1[0] * k
                        yield (pos[0], k * pos[0] + b), ag_obj

    def snap_nearest_point_2(self, pos):
        point, dist, ag_obj_res = pos, 10000, None
        for obj, ag_obj in self.get_screen_objects(self.plane):
            if isinstance(obj, ScreenPoint2) and (d := distance(pos, obj.tuple())) < dist and (
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
        print(self.intersections_xy, self.intersections_xz)


class Snap:
    def __init__(self, func, image):
        self.func = func
        self.name = image
        # self.image = pg.image.load('images/snap_' + image + '.bmp')
        # self.image.set_colorkey((255, 255, 255))

    def draw(self, screen):
        pass
        # screen.screen.blit(self.image, (pos[0] - 8, pos[1] - 8))

    def __str__(self):
        return 'Snap ' + self.name


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def nearest_point(point, segment, as_line=False):
    if segment.p1[0] - segment.p2[0] == 0:
        k1 = 100000000000
    else:
        k1 = (segment.p1[1] - segment.p2[1]) / (segment.p1[0] - segment.p2[0])
    b1 = segment.p1[1] - segment.p1[0] * k1
    if k1 != 0:
        k2 = -1 / k1
    else:
        k2 = 100000000000
    b2 = point[1] - point[0] * k2
    intersection_point = (b2 - b1) / (k1 - k2)
    intersection_point = intersection_point, k1 * intersection_point + b1
    if as_line:
        return intersection_point
    if min(segment.p1[0], segment.p2[0]) < intersection_point[0] < max(segment.p1[0], segment.p2[0]):
        return intersection_point
    elif distance(point, segment.p1) < distance(point, segment.p2):
        return segment.p1
    return segment.p2
