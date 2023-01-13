class ScreenCircle:
    def __init__(self, plot, center, radius, color=(0, 0, 0)):
        self.center = center
        self.radius = radius
        self.plot = plot
        self.color = color

    def tuple(self):
        return self.center, self.radius

    def draw(self):
        self.plot.draw_circle(self, self.color)
