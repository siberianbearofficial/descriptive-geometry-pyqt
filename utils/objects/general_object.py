from uuid import uuid4

import core.angem as ag
import utils.history.serializable as serializable
import utils.drawing.projections.projection_manager as projections
from utils.color import *
from utils.thickness import *

ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alph = ALPH.lower()
used_names = set()
used_points = set()

SEP = '-'


class GeneralObject:
    serializable = ('name', 'ag_object', 'color', 'thickness', 'config')

    def __init__(self, ag_object, layer_id, color: ObjectColor = LAYER_COLOR, name='', thickness=4, **kwargs):
        self.ag_object = ag_object
        self.layer_id = layer_id
        self.color = color
        self.name = name
        self.thickness = Thickness.fix(thickness)
        self.config = set_config(ag_object, kwargs)

        self.generate_name()
        self.id = uuid4()

        self.xy_projections = []
        self.xz_projections = []
        self.connection_lines = []
        self.update_projections()

    def delete(self):
        if self.name in used_names:
            used_names.remove(self.name)

    def generate_name(self):
        if self.name is None:
            self.name = 'A'
            return
        if self.name == 'GENERATE':
            i, ag_class = 1, self.ag_object.__class__.__name__
            while True:
                if ag_class + ' ' + str(i) not in used_names:
                    self.name = ag_class + ' ' + str(i)
                    used_names.add(self.name)
                    break
                i += 1
        else:
            while '__UPPER__' in self.name:
                self.name = self.name.replace('__UPPER__', GeneralObject.get_alpha(), 1)
            while '__lower__' in self.name:
                self.name = self.name.replace('__lower__', GeneralObject.get_alpha(lower=True), 1)
        if isinstance(self.ag_object, ag.Point):
            used_points.add(self.name)
        elif isinstance(self.ag_object, ag.Segment) and self.name.count(SEP) == 1:
            for el in self.name.split(SEP):
                used_points.add(el)
        elif isinstance(self.ag_object, ag.Plane) and self.config.get('draw_3p', False) and self.name.count(SEP) == 2:
            for el in self.name.split(SEP):
                used_points.add(el)

    def __setattr__(self, key, value):
        if key == 'name' and 'name' in self.__dict__:
            if self.name is None:
                return
            if isinstance(self.ag_object, ag.Point):
                used_points.discard(self.name)
                used_points.add(value)
            elif isinstance(self.ag_object, ag.Segment):
                if self.name.count(SEP) == 1:
                    for el in self.name.split(SEP):
                        used_points.discard(el)
                if value.count(SEP) == 1:
                    for el in value.split(SEP):
                        used_points.add(el)
            elif isinstance(self.ag_object, ag.Plane) and self.config.get('draw_3p', False):
                if self.name.count(SEP) == 2:
                    for el in self.name.split(SEP):
                        used_points.discard(el)
                if value.count(SEP) == 2:
                    for el in value.split(SEP):
                        used_points.add(el)
            used_names.discard(self.name)
            used_names.add(value)
        super(GeneralObject, self).__setattr__(key, value)

    def __del__(self):
        pass
        # if isinstance(self.ag_object, ag.Point):
        #     used_points.discard(self.name)
        # elif isinstance(self.ag_object, ag.Segment):
        #     if self.name.count(SEP) == 1:
        #         for el in self.name.split(SEP):
        #             used_points.discard(el)
        # elif isinstance(self.ag_object, ag.Plane) and self.config.get('draw_3p', False):
        #     if self.name.count(SEP) == 2:
        #         for el in self.name.split(SEP):
        #             used_points.discard(el)
        # used_names.discard(self.name)

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
                if symbol not in used_points:
                    used_names.add(symbol)
                    return symbol
            i, s = 1, '1'
            while True:
                for symbol in ALPH:
                    if symbol + s not in used_points:
                        used_names.add(symbol + s)
                        return symbol + s
                i += 1
                s = str(i)

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

        return {'name': self.name, 'color': str(self.color), 'ag_object': convert(self.ag_object),
                'thickness': self.thickness, 'config': self.config}

    @staticmethod
    def from_dict(dct: dict):
        """
        Function that creates general object from the given dictionary.
        :param dct: dictionary
        :return: general object
        """

        # Checking if it is possible to create a general object
        if 'ag_object' not in dct:
            raise ValueError(f'Unable to create GeneralObject, no such field in the given dictionary: ag_object.')

        # Creating GeneralObject
        ag_object = unpack_ag_object(dct['ag_object'])
        if 'config' in dct and isinstance(dct['config'], dict):
            general_object = GeneralObject(ag_object, **dct['config'])
        else:
            general_object = GeneralObject(ag_object)

        if 'name' in dct and isinstance(dct['name'], str):
            general_object.name = dct['name']
        if 'color' in dct and Color.valid(dct['color']):
            general_object.color = Color(dct['color'])
        if 'thickness' in dct and (
                (isinstance(dct['thickness'], str) and dct['thickness'].isdigit()) or isinstance(dct['thickness'],
                                                                                                 int)):
            general_object.thickness = int(dct['thickness'])

        return general_object

    def set_name(self, name):
        if name == self.name:
            return False
        self.name = name
        return True

    def set_color(self, color):
        if color != self.color:
            self.color = color
            return True
        return False

    def set_thickness(self, thickness):
        if thickness != self.thickness:
            self.thickness = thickness
            return True
        return False

    def set_config(self, config):
        if config != self.config:
            self.config = config
            return True
        return False

    def set_ag_object(self, dct):
        if dct != self.to_dict()['ag_object']:
            self.ag_object = unpack_ag_object(dct)
            return True
        return False

    def update_projections(self):
        self.xy_projections, self.xz_projections, self.connection_lines = projections.get_projection(
            self.ag_object, self.color, self.thickness)
        if not isinstance(self.xy_projections, (tuple, list)):
            self.xy_projections = (self.xy_projections,)
        if not isinstance(self.xz_projections, (tuple, list)):
            self.xz_projections = (self.xz_projections,)
        if not isinstance(self.connection_lines, (tuple, list)):
            self.connection_lines = (self.connection_lines,)


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
        if 'class' in obj and isinstance(obj['class'], str):
            cls = serializable.angem_class_by_name[obj['class']]
            return cls(*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[cls]])
        return obj['class'](*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[obj['class']]])
