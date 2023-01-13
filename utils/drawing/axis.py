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
        self.lp = ScreenPoint(self.plot, self.plot.tlp[0], (self.plot.brp[1] + self.plot.tlp[1]) // 2, self.color)
        self.rp = ScreenPoint(self.plot, self.plot.brp[0], (self.plot.brp[1] + self.plot.tlp[1]) // 2, self.color)
        self.segment = ScreenSegment(self.plot, self.lp, self.rp, self.color)

    def update(self, plot):
        self.plot = plot
        self.dimensions()

    def draw(self):
        self.segment.draw()
