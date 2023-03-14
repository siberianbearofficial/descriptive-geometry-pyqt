from utils.drawing.projections.projection_manager import ScreenPoint


class ScreenCircle:
    def __init__(self, plot, center, radius, color=(0, 0, 0), thickness=2):
        if isinstance(center, ScreenPoint):
            center = center.list()
        elif isinstance(center, tuple):
            center = list(center)
        self.center = center
        self.radius = int(radius)
        self.plot = plot
        self.color = color
        self.thickness = thickness

    def tuple(self):
        return self.center, self.radius

    def draw(self, color=None, thickness=-1):
        if thickness == -1:
            thickness = self.thickness
        if color is None:
            color = self.color
        self.plot.draw_circle(self.center, self.radius, color, thickness)

    def move(self, x, y):
        self.center[0] += x
        self.center[1] += y

