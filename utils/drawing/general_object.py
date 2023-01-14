class GeneralObject:
    def __init__(self, plot, ag_object, color):
        self.ag_object = ag_object
        self.plot = plot
        self.color = color
        self.xy_projection = plot.pm.get_projection(ag_object, 'xy', color)
        if not isinstance(self.xy_projection, tuple):
            self.xy_projection = self.xy_projection,
        self.xz_projection = plot.pm.get_projection(ag_object, 'xz', color)
        if not isinstance(self.xz_projection, tuple):
            self.xz_projection = self.xz_projection,

    def draw(self):
        for el in self.xy_projection:
            el.draw()
        for el in self.xz_projection:
            el.draw()

    def update_projections(self):
        self.xy_projection = self.plot.pm.get_projection(self.ag_object, 'xy', self.color)
        if not isinstance(self.xy_projection, tuple):
            self.xy_projection = self.xy_projection,
        self.xz_projection = self.plot.pm.get_projection(self.ag_object, 'xz', self.color)
        if not isinstance(self.xz_projection, tuple):
            self.xz_projection = self.xz_projection,
