import utils.maths.angem as ag
import utils.history.serializable as serializable
from utils.drawing.object_name_bar import ObjectNameBar, get_name_bar_text, get_name_bar_pos

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

        self.generate_name()

        if xy_projection is None or xz_projection is None:
            self.xy_projection, self.xz_projection, self.connection_lines = self.projections()
        else:
            self.xy_projection = xy_projection
            self.xz_projection = xz_projection

        self.name_bars = self.set_name_bars()

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
        for bar, pos in zip(self.name_bars, get_name_bar_pos(self)):
            if pos is None:
                bar.hide()
            else:
                bar.show()
                bar.move3(*pos[0], pos[1])

    def move(self, x, y):
        if isinstance(self.ag_object, ag.Line) or \
                isinstance(self.ag_object, ag.Plane) and self.config.get('draw_3p', False):
            self.update_projections()
            return
        for el in self.xy_projection:
            el.move(x, y)
        for el in self.xz_projection:
            el.move(x, y)
        for el in self.connection_lines:
            el.move(x, y)
        for el in self.name_bars:
            el.move2(x, y)

    def generate_name(self):
        if self.name == 'GENERATE':
            # TODO: check if all names used
            global indexU, indexL, alph, ALPH
            if isinstance(self.ag_object, ag.Point):
                while ALPH[indexU] not in used_names:
                    self.name = ALPH[indexU]
                    used_names.add(self.name)
                indexU += 1
                indexU %= len(ALPH)
            elif isinstance(self.ag_object, ag.Segment):
                s = '!'
                while ALPH[indexU] not in used_names:
                    s = ALPH[indexU]
                    used_names.add(s)
                indexU += 1
                indexU %= len(ALPH)
                while ALPH[indexU] not in used_names:
                    self.name = s + SEP + ALPH[indexU]
                    used_names.add(ALPH[indexU])
                indexU += 1
                indexU %= len(ALPH)
            elif isinstance(self.ag_object, ag.Line) or isinstance(self.ag_object, ag.Plane):
                while alph[indexL] not in used_names:
                    self.name = alph[indexL]
                    used_names.add(self.name)
                indexL += 1
                indexL %= len(alph)

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

        return GeneralObject(plot, unpack_ag_object(dct['ag_object']), dct['color'], dct['name'], **dct['config'])

    def set_name_bars(self):
        text = get_name_bar_text(self)
        pos = get_name_bar_pos(self)
        return tuple(ObjectNameBar(self.plot, *pos[i], text[i]) for i in range(len(pos)))

    def destroy_name_bars(self):
        for el in self.name_bars:
            el.hide()
            el.destroy()

    def hide_name_bars(self):
        for el in self.name_bars:
            el.hide()

    def show_name_bars(self):
        for el in self.name_bars:
            el.show()

    def set_name(self, name):
        self.name = name
        self.destroy_name_bars()
        self.name_bars = self.set_name_bars()


def set_config(obj, config):
    if isinstance(obj, ag.Point) or isinstance(obj, ag.Point) or \
            isinstance(obj, ag.Point) and config.get('draw_3p', False):
        config['draw_cl'] = True

    return config
