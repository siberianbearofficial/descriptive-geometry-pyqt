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
