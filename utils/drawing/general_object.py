import utils.maths.angem as ag
import utils.history.serializable as serializable
from utils.drawing.object_name_bar import ObjectNameBar, get_name_bar_text, get_name_bar_pos

indexU, indexL = 0, 0
ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alph = ALPH.lower()
used_names = set()

SEP = '-'


class GeneralObject:
    def __init__(self, plot, ag_object=None, color=(0, 0, 0), name='', xy_projection=None, xz_projection=None):
        self.ag_object = ag_object
        self.plot = plot
        self.color = color
        self.name = name

        self.generate_name()

        if xy_projection is None or xz_projection is None:
            self.xy_projection, self.xz_projection = self.projections()
        else:
            self.xy_projection = xy_projection
            self.xz_projection = xz_projection

        self.name_bars = self.set_name_bars()

    def draw(self):
        for el in self.xy_projection:
            el.draw()
        for el in self.xz_projection:
            el.draw()

    def draw_qt(self, selected=False):
        if selected:
            for el in self.xy_projection:
                el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
            for el in self.xz_projection:
                el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
        for el in self.xy_projection:
            el.draw_qt()
        for el in self.xz_projection:
            el.draw_qt()

    def projections(self):
        xy_projection = self.plot.pm.get_projection(self.ag_object, 'xy', self.color)
        if not isinstance(xy_projection, (tuple, list)):
            xy_projection = xy_projection,
        xz_projection = self.plot.pm.get_projection(self.ag_object, 'xz', self.color)
        if not isinstance(xz_projection, (tuple, list)):
            xz_projection = xz_projection,
        return xy_projection, xz_projection

    def update_projections(self):
        self.xy_projection, self.xz_projection = self.projections()
        for bar, pos in zip(self.name_bars, get_name_bar_pos(self)):
            if pos is None:
                bar.hide()
            else:
                bar.show()
                bar.move3(*pos[0], pos[1])

    def move(self, x, y):
        if isinstance(self.ag_object, ag.Line) or isinstance(self.ag_object, ag.Plane):
            self.update_projections()
            return
        for el in self.xy_projection:
            el.move(x, y)
        for el in self.xz_projection:
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

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, int) or isinstance(obj, float):
                return obj
            if isinstance(obj, list) or isinstance(obj, tuple):
                return list(map(convert, obj))
            dct = obj.__dict__
            res = {'class': obj.__class__}
            for key in serializable.angem_objects[obj.__class__]:
                res[key] = convert(dct[key])
            return res

        return {'name': self.name, 'color': self.color, 'ag_object': convert(self.ag_object)}

    @staticmethod
    def from_dict(plot, dct):
        def unpack_ag_object(obj):
            if isinstance(obj, int) or isinstance(obj, float):
                return obj
            if isinstance(obj, list) or isinstance(obj, tuple):
                return list(map(unpack_ag_object, obj))
            if isinstance(obj, dict):
                return obj['class'](*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[obj['class']]])

        return GeneralObject(plot, unpack_ag_object(dct['ag_object']), dct['color'], dct['name'])

    def set_name_bars(self):
        text = get_name_bar_text(self)
        pos = get_name_bar_pos(self)
        return tuple(ObjectNameBar(self.plot, *pos[i], text[i]) for i in range(len(pos)))

    def destroy_name_bars(self):
        for el in self.name_bars:
            el.hide()
