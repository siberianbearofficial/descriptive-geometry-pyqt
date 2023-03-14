import core.angem as ag


class PlotObject:
    def __init__(self, plot, general_object):
        self.general_object = general_object
        self.id = general_object.id
        self.plot = plot
        self.ag_object = general_object.ag_object
        self.name = general_object.name
        self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
        if self.general_object.name:
            self.labels = self.plot.lm.add_labels_to_obj(self)
        else:
            self.labels = tuple()

    def __del__(self):
        self.destroy_name_bars()

    def draw(self, selected=0):
        for el in self.connection_lines:
            el.draw()
        if selected:
            if selected == 1:
                for el in self.xy_projection:
                    el.draw(color=(250, 30, 30), thickness=(el.thickness + 2))
                for el in self.xz_projection:
                    el.draw(color=(250, 30, 30), thickness=(el.thickness + 2))
                for el in self.xy_projection:
                    el.draw()
                for el in self.xz_projection:
                    el.draw()
            elif selected == 2:
                for el in self.xy_projection:
                    el.draw(thickness=(el.thickness + 2))
                for el in self.xz_projection:
                    el.draw(thickness=(el.thickness + 2))
        else:
            for el in self.xy_projection:
                el.draw()
            for el in self.xz_projection:
                el.draw()

    def projections(self):
        proj = self.plot.pm.get_projection(self.general_object.ag_object, self.general_object.color,
                                           **self.general_object.config)
        xy_projection, xz_projection = proj[0], proj[1]
        connection_lines = proj[2] if len(proj) >= 3 else tuple()
        if not isinstance(xy_projection, (tuple, list)):
            xy_projection = xy_projection,
        if not isinstance(xz_projection, (tuple, list)):
            xz_projection = xz_projection,
        if not isinstance(connection_lines, (tuple, list)):
            connection_lines = connection_lines,
        return xy_projection, xz_projection, connection_lines

    def update_projections(self):
        self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
        self.destroy_name_bars()
        self.set_name_bars()

    def replace_general_object(self, general_object):
        self.general_object = general_object
        self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
        if self.general_object.name:
            self.labels = self.plot.lm.add_labels_to_obj(self)

    def move(self, x, y):
        if isinstance(self.general_object.ag_object, ag.Line) or \
                isinstance(self.general_object.ag_object, ag.Plane) and not \
                self.general_object.config.get('draw_3p', False):
            self.update_projections()
            return
        for el in self.xy_projection:
            el.move(x, y)
        for el in self.xz_projection:
            el.move(x, y)
        for el in self.connection_lines:
            el.move(x, y)

    def delete(self):
        self.destroy_name_bars()

    # @staticmethod
    # def get_alpha(lower=False):
    #     if lower:
    #         for symbol in alph:
    #             if symbol not in used_names:
    #                 used_names.add(symbol)
    #                 return symbol
    #         i, s = 1, '1'
    #         while True:
    #             for symbol in alph:
    #                 if symbol + s not in used_names:
    #                     used_names.add(symbol + s)
    #                     return symbol + s
    #             i += 1
    #             s = str(i)
    #     else:
    #         for symbol in ALPH:
    #             if symbol not in used_names:
    #                 used_names.add(symbol)
    #                 return symbol
    #         i, s = 1, '1'
    #         while True:
    #             for symbol in ALPH:
    #                 if symbol + s not in used_names:
    #                     used_names.add(symbol + s)
    #                     return symbol + s
    #             i += 1
    #             s = str(i)
    #
    # def name_to_point(self, pos):
    #     name = self.plot.lm.get_name_to_new_obj(pos)
    #     if name:
    #         return name
    #     return GeneralObject.get_alpha()

    def set_name_bars(self):
        self.labels = self.plot.lm.add_labels_to_obj(self)

    def destroy_name_bars(self):
        for pos, text in self.labels:
            self.plot.lm.delete_label(pos, text)


class TempObject:
    def __init__(self, plot, ag_object=None, color=(0, 0, 0)):
        self.plot = plot
        self.ag_object = ag_object
        self.color = color
        self.thickness = 1
        self.xy_projection, self.xz_projection, self.connection_lines = self.projections()

    def projections(self):
        proj = self.plot.pm.get_projection(self.ag_object, self.color)
        xy_projection, xz_projection = proj[0], proj[1]
        connection_lines = proj[2] if len(proj) >= 3 else tuple()
        if not isinstance(xy_projection, (tuple, list)):
            xy_projection = xy_projection,
        if not isinstance(xz_projection, (tuple, list)):
            xz_projection = xz_projection,
        if not isinstance(connection_lines, (tuple, list)):
            connection_lines = connection_lines,
        return xy_projection, xz_projection, connection_lines

    def draw(self):
        for el in self.connection_lines:
            el.draw()
        else:
            for el in self.xy_projection:
                el.draw()
            for el in self.xz_projection:
                el.draw()
