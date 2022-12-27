class ScreenSegment:
    def __init__(self, plot, p1, p2, color=(0, 0, 0)):
        self.p1 = p1
        self.p2 = p2
        self.plot = plot
        self.color = color

    def draw(self):
        self.plot.draw_segment(self, self.color)
