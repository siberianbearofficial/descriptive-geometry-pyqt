from utils.drawing.screen_point import ScreenPoint
from math import inf


class ScreenSegment:
    def __init__(self, plot, p1, p2, color=(0, 0, 0), thickness=3, line_type=1):
        if isinstance(p1, ScreenPoint):
            p1 = p1.list()
        elif isinstance(p1, tuple):
            p1 = list(p1)
        if isinstance(p2, ScreenPoint):
            p2 = p2.list()
        elif isinstance(p2, tuple):
            p2 = list(p2)
        self.p1 = p1
        self.p2 = p2
        self.plot = plot
        self.color = color
        self.thickness = thickness
        self.line_type = line_type
        if self.p2[0] != self.p1[0]:
            self.k = ((self.p2[1] - self.p1[1]) / (self.p2[0] - self.p1[0]))
            self.b = p1[1] - self.k * p1[0]
            self.x1 = min(p1[0], p2[0])
            self.x2 = max(p1[0], p2[0])
            if self.k > 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.tlp[1] + 2))
                self.p1_by_y = self.x(self.plot.tlp[1] + 2) < self.plot.tlp[0] + 2
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.brp[1] - 2))
                self.p2_by_y = self.x(self.plot.brp[1] - 2) > self.plot.brp[0] - 2
            elif self.k < 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.brp[1] - 2))
                self.p1_by_y = self.x(self.plot.brp[1] - 2) < self.plot.tlp[0] + 2
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.tlp[1] + 2))
                self.p2_by_y = self.x(self.plot.tlp[1] + 2) > self.plot.brp[0] - 2
            elif self.plot.tlp[1] < p1[1] < self.plot.brp[1]:
                min_x = max(self.x1, self.plot.tlp[0] + 2)
                self.p1_by_y = True
                max_x = min(self.x2, self.plot.brp[0] - 2)
                self.p2_by_y = True
            else:
                self.drawing = False
                self.p1_by_y = False
                self.p2_by_y = False
                return
            if min_x > max_x:
                self.drawing = False
            else:
                self.drawing = True
                self.point1 = int(min_x), int(self.y(min_x))
                self.point2 = int(max_x), int(self.y(max_x))
        else:
            self.k = None
            self.b = None
            self.p1_by_y = True
            self.p2_by_y = True
            self.y1 = min(p1[1], p2[1])
            self.y2 = max(p1[1], p2[1])
            min_y = max(self.y1, self.plot.tlp[1] + 2)
            max_y = min(self.y2, self.plot.brp[1] - 2)
            if min_y <= max_y and self.plot.tlp[0] < p1[0] < self.plot.brp[0]:
                self.drawing = True
                self.point1 = int(p1[0]), int(min_y)
                self.point2 = int(p1[0]), int(max_y)
            else:
                self.drawing = False

    def draw(self, color=None, thickness=-1):
        if thickness == -1:
            thickness = self.thickness
        if color is None:
            color = self.color
        if self.drawing and self.point1 != self.point2:
            self.plot.draw_segment(self.point1, self.point2, color, thickness, self.line_type)

    def y(self, x):
        return self.k * x + self.b

    def x(self, y):
        if self.k is None:
            return self.p1[0]
        return (y - self.b) / self.k

    def move(self, x, y):
        self.p1[0] += x
        self.p1[1] += y
        self.p2[0] += x
        self.p2[1] += y
        if self.k is None:
            self.y1 += y
            self.y2 += y
            min_y = max(self.y1, self.plot.tlp[1] + 2)
            max_y = min(self.y2, self.plot.brp[1] - 2)
            if min_y <= max_y and self.plot.tlp[0] < self.p1[0] < self.plot.brp[0]:
                self.drawing = True
                self.point1 = int(self.p1[0]), int(min_y)
                self.point2 = int(self.p1[0]), int(max_y)
            else:
                self.drawing = False
        else:
            self.b = self.p1[1] - self.k * self.p1[0]
            self.x1 += x
            self.x2 += x
            if self.k > 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.tlp[1] + 2))
                self.p1_by_y = self.x(self.plot.tlp[1] + 2) > self.plot.tlp[0] + 2
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.brp[1] - 2))
                self.p2_by_y = self.x(self.plot.brp[1] - 2) > self.plot.brp[0] - 2
            elif self.k < 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.brp[1] - 2))
                self.p1_by_y = self.x(self.plot.brp[1] - 2) > self.plot.tlp[0] + 2
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.tlp[1] + 2))
                self.p2_by_y = self.x(self.plot.tlp[1] + 2) > self.plot.brp[0] - 2
            elif self.plot.tlp[1] < self.p1[1] < self.plot.brp[1]:
                min_x = max(self.x1, self.plot.tlp[0] + 2)
                self.p1_by_y = True
                max_x = min(self.x2, self.plot.brp[0] - 2)
                self.p2_by_y = True
            else:
                self.drawing = False
                return
            if min_x > max_x:
                self.drawing = False
            else:
                self.drawing = True
                self.point1 = int(min_x), int(self.y(min_x))
                self.point2 = int(max_x), int(self.y(max_x))
