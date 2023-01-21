import utils.maths.angem as ag


class GeneralObject:
    def __init__(self, plot, ag_object=None, color=(0, 0, 0), xy_projection=None, xz_projection=None):
        self.ag_object = ag_object
        self.plot = plot
        self.color = color
        if xy_projection is None or xz_projection is None:
            self.xy_projection, self.xz_projection = self.projections()
        else:
            self.xy_projection = xy_projection
            self.xz_projection = xz_projection

    def draw(self):
        for el in self.xy_projection:
            el.draw()
        for el in self.xz_projection:
            el.draw()

    def projections(self):
        xy_projection = self.plot.pm.get_projection(self.ag_object, 'xy', self.color)
        if not isinstance(xy_projection, tuple):
            xy_projection = xy_projection,
        xz_projection = self.plot.pm.get_projection(self.ag_object, 'xz', self.color)
        if not isinstance(xz_projection, tuple):
            xz_projection = xz_projection,
        return xy_projection, xz_projection

    def update_projections(self):
        self.xy_projection, self.xz_projection = self.projections()

    def move(self, x, y):
        if isinstance(self.ag_object, ag.Line):
            self.xy_projection, self.xz_projection = self.projections()
            return
        self.xy_projection, self.xz_projection = self.projections()
        for el in self.xy_projection:
            el.move(x, y)
        for el in self.xz_projection:
            el.move(x, y)
