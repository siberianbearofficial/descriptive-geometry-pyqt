class ScreenPoint:
    def __init__(self, plot, x, y, color=(0, 0, 0), thickness=3):
        self.x = x
        self.y = y
        self.plot = plot
        self.color = color
        self.thickness = thickness

    def tuple(self):
        return self.x, self.y

    def draw(self):
        self.plot.draw_point(self, self.color)

    def draw_qt(self, color=None, thickness=-1):
        if thickness == -1:
            thickness = self.thickness
        if color is None:
            color = self.color
        self.plot.draw_point(self.tuple(), color, thickness)

    def move(self, x, y):
        self.x += x
        self.y += y


class ScreenPoint2:
    def __init__(self, plot, x, y, color=(0, 0, 0), thickness=2):
        self.x = x
        self.y = y
        self.plot = plot
        self.color = color
        self.thickness = thickness

    def tuple(self):
        return self.x, self.y

    def draw(self):
        self.plot.draw_point2(self, self.color)

    def draw_qt(self, color=None, thickness=-1):
        if thickness == -1:
            thickness = self.thickness
        if color is None:
            color = self.color
        self.plot.draw_point2(self.tuple(), color, thickness)

    def move(self, x, y):
        self.x += x
        self.y += y

