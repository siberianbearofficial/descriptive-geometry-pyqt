import utils.maths.angem as ag
import utils.history.serializable as serializable

indexU, indexL = 0, 0
ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alph = ALPH.lower()
used_names = set()

SEP = '-'


class GeneralObject:
    def __init__(self, plot, ag_object=None, color=(0, 0, 0), name='', xy_projection=None, xz_projection=None,
                 **kwargs):
        self.ag_object = ag_object
        self.plot = plot
        self.color = color
        self.name = name
        self.thickness = 1
        self.config = set_config(ag_object, kwargs)

        if xy_projection is None or xz_projection is None:
            self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
        else:
            self.xy_projection = xy_projection
            self.xz_projection = xz_projection

        self.generate_name()
        if self.name:
            self.labels = self.plot.lm.add_labels_to_obj(self)

    def draw(self):
        for el in self.xy_projection:
            el.draw()
        for el in self.xz_projection:
            el.draw()

    def draw_qt(self, selected=0):
        for el in self.connection_lines:
            el.draw_qt()
        if selected:
            if selected == 1:
                for el in self.xy_projection:
                    el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
                for el in self.xz_projection:
                    el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
                for el in self.xy_projection:
                    el.draw_qt()
                for el in self.xz_projection:
                    el.draw_qt()
            elif selected == 2:
                for el in self.xy_projection:
                    el.draw_qt(thickness=(el.thickness + 2))
                for el in self.xz_projection:
                    el.draw_qt(thickness=(el.thickness + 2))
        else:
            for el in self.xy_projection:
                el.draw_qt()
            for el in self.xz_projection:
                el.draw_qt()

    def projections(self):
        proj = self.plot.pm.get_projection(self.ag_object, self.color, **self.config)
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

    def move(self, x, y):
        if isinstance(self.ag_object, ag.Line) or \
                isinstance(self.ag_object, ag.Plane) and not self.config.get('draw_3p', False):
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
        if self.name in used_names:
            used_names.remove(self.name)

    def generate_name(self):
        if self.name == 'GENERATE':
            # TODO: check if all names used
            if isinstance(self.ag_object, ag.Point):
                self.name = self.name_to_point(self.xy_projection[0].tuple())
            elif isinstance(self.ag_object, ag.Segment):
                self.name = self.name_to_point(self.xy_projection[0].p1) + SEP + \
                            self.name_to_point(self.xy_projection[0].p2)
            elif isinstance(self.ag_object, ag.Plane) and self.config.get('draw_3p', False):
                self.name = self.name_to_point(self.xy_projection[3].tuple()) + SEP + \
                            self.name_to_point(self.xy_projection[4].tuple()) + SEP + \
                            self.name_to_point(self.xy_projection[5].tuple())
            elif isinstance(self.ag_object, ag.Line) or isinstance(self.ag_object, ag.Plane):
                self.name = GeneralObject.get_alpha(lower=True)
            else:
                i, ag_class = 1, self.ag_object.__class__.__name__
                while True:
                    if ag_class + ' ' + str(i) not in used_names:
                        self.name = ag_class + ' ' + str(i)
                        used_names.add(self.name)
                        break
                    i += 1

    @staticmethod
    def get_alpha(lower=False):
        if lower:
            for symbol in alph:
                if symbol not in used_names:
                    used_names.add(symbol)
                    return symbol
            i, s = 1, '1'
            while True:
                for symbol in alph:
                    if symbol + s not in used_names:
                        used_names.add(symbol + s)
                        return symbol + s
                i += 1
                s = str(i)
        else:
            for symbol in ALPH:
                if symbol not in used_names:
                    used_names.add(symbol)
                    return symbol
            i, s = 1, '1'
            while True:
                for symbol in ALPH:
                    if symbol + s not in used_names:
                        used_names.add(symbol + s)
                        return symbol + s
                i += 1
                s = str(i)

    def name_to_point(self, pos):
        name = self.plot.lm.get_name_to_new_obj(pos)
        if name:
            return name
        return GeneralObject.get_alpha()

    def to_dict(self, class_names=False):
        def convert(obj):
            if isinstance(obj, int) or isinstance(obj, float):
                return obj
            if isinstance(obj, list) or isinstance(obj, tuple):
                return list(map(convert, obj))
            dct = obj.__dict__
            if class_names:
                res = {'class': obj.__class__.__name__}
            else:
                res = {'class': obj.__class__}
            for key in serializable.angem_objects[obj.__class__]:
                res[key] = convert(dct[key])
            return res

        return {'name': self.name, 'color': self.color, 'ag_object': convert(self.ag_object), 'config': self.config}

    @staticmethod
    def from_dict(plot, dct):
        return GeneralObject(plot, unpack_ag_object(dct['ag_object']), dct['color'], dct['name'], **dct['config'])

    def set_name_bars(self):
        self.labels = self.plot.lm.add_labels_to_obj(self)

    def destroy_name_bars(self):
        for pos, text in self.labels:
            self.plot.lm.delete_label(pos, text)

    def set_name(self, name):
        if name == self.name:
            return False
        self.name = name
        self.destroy_name_bars()
        self.set_name_bars()
        return True

    def set_color(self, color):
        if color != self.color:
            self.color = color
            for el in self.xy_projection:
                el.color = color
            for el in self.xz_projection:
                el.color = color
            return True
        return False

    def set_thickness(self, thickness):
        if thickness != self.thickness:
            print('THICKNESS', thickness)
            self.thickness = thickness
            return True
        return False

    def set_config(self, config):
        if config != self.config:
            self.config = config
            self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
            return True
        return False

    def set_ag_object(self, dct):
        if dct != self.to_dict()['ag_object']:
            self.ag_object = unpack_ag_object(dct)
            self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
            return True
        return False


def set_config(obj, config):
    if isinstance(obj, ag.Point) or isinstance(obj, ag.Point) or \
            isinstance(obj, ag.Point) and config.get('draw_3p', False):
        config['draw_cl'] = True

    return config


def unpack_ag_object(obj):
    if isinstance(obj, int) or isinstance(obj, float):
        return obj
    if isinstance(obj, list) or isinstance(obj, tuple):
        return list(map(unpack_ag_object, obj))
    if isinstance(obj, dict):
        if isinstance(obj['class'], str):
            cls = serializable.angem_class_by_name[obj['class']]
            return cls(*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[cls]])
        return obj['class'](*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[obj['class']]])

