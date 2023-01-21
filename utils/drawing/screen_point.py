class ScreenPoint:
    def __init__(self, plot, x, y, color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.plot = plot
        self.color = color

    def tuple(self):
        return self.x, self.y

    def draw(self):
        self.plot.draw_point(self, self.color)

    def move(self, x, y):
        self.x += x
        self.y += y


class ScreenPoint2:
    def __init__(self, plot, x, y, color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.plot = plot
        self.color = color

    def tuple(self):
        return self.x, self.y

    def draw(self):
        self.plot.draw_point2(self, self.color)

    def move(self, x, y):
        self.x += x
        self.y += y

