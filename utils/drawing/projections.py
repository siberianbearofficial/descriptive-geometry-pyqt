import utils.maths.angem as ag
from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment


class ProjectionManager:

    def __init__(self, plot):
        self.plot = plot
        self.axis = plot.axis

    def get_projection(self, obj, plane, color):
        if isinstance(obj, ag.Point):
            return ScreenPoint(self.plot, *self.convert_ag_coordinate_to_screen_coordinate(obj.x, obj.y, obj.z, plane),
                               color)
        elif isinstance(obj, ag.Segment):
            p1 = ScreenPoint(self.plot,
                             *self.convert_ag_coordinate_to_screen_coordinate(obj.p1.x, obj.p1.y, obj.p1.z, plane),
                             color)
            p2 = ScreenPoint(self.plot,
                             *self.convert_ag_coordinate_to_screen_coordinate(obj.p2.x, obj.p2.y, obj.p2.z, plane),
                             color)
            return ScreenSegment(self.plot, p1, p2, color)
        elif isinstance(obj, ag.Line):
            # TODO: check for projection of a line to a point
            if plane == 'xy':
                if obj.vector.y == 0:
                    return self.get_projection(
                        obj.cut_by_x(self.convert_screen_x_to_ag_x(self.plot.brp[0]),
                                     self.convert_screen_x_to_ag_x(self.plot.tlp[0])),
                        plane, color)
                else:
                    return self.get_projection(
                        obj.cut_by_y(self.convert_screen_y_to_ag_y(self.axis.lp.y),
                                     self.convert_screen_y_to_ag_y(self.plot.brp[1])),
                        plane, color)
            else:
                if obj.vector.z == 0:
                    return self.get_projection(
                        obj.cut_by_x(self.convert_screen_x_to_ag_x(self.plot.brp[0]),
                                     self.convert_screen_x_to_ag_x(self.plot.tlp[0])),
                        plane, color)
                else:
                    return self.get_projection(
                        obj.cut_by_z(self.convert_screen_y_to_ag_z(self.axis.lp.y),
                                     self.convert_screen_y_to_ag_z(self.plot.tlp[1])),
                        plane, color)

    def convert_ag_coordinate_to_screen_coordinate(self, x, y=None, z=None, plane='xy'):
        if plane == 'xy':
            return self.axis.rp.x - x, y + self.axis.lp.y
        return self.axis.rp.x - x, self.axis.lp.y - z

    def convert_screen_x_to_ag_x(self, x):
        return self.axis.rp.x - x

    def convert_screen_y_to_ag_y(self, y):
        return y - self.axis.lp.y

    def convert_screen_y_to_ag_z(self, z):
        return self.axis.lp.y - z
