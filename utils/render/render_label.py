

class RenderLabel:
    def __init__(self, plot, text, pos):
        self.plot = plot
        self.text = " = ".join(set(text))
        self.pos = pos

    def draw(self):
        self.plot.draw_text((self.pos[0] + 10, self.pos[1] - 10), self.text)

    def move(self, x, y):
        self.pos[0] += x
        self.pos[1] += y
