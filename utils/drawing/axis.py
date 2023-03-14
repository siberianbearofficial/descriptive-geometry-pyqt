from utils.drawing.screen_point import ScreenPoint
from utils.drawing.screen_segment import ScreenSegment


class Axis:

    def __init__(self, plot, color=(0, 0, 0)):
        self.plot = plot
        self.color = color
        self.lp = None
        self.rp = None
        self.segment = None
        self.dimensions()

    def dimensions(self):
        self.lp = [self.plot.tlp[0], (self.plot.brp[1] + self.plot.tlp[1]) // 2]
        self.rp = [self.plot.brp[0] - 1, (self.plot.brp[1] + self.plot.tlp[1]) // 2]
        self.segment = ScreenSegment(self.plot, self.lp, self.rp, self.color)

    def update(self, plot):
        self.plot = plot
        self.dimensions()

    def draw(self):
        self.segment.draw()

    def move(self, x, y):
        self.lp[1] += y
        self.rp[1] += y
        self.segment.point1 = self.segment.point1[0], self.segment.point1[1] + y
        self.segment.point2 = self.segment.point2[0], self.segment.point2[1] + y
