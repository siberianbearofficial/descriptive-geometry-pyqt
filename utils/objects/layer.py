from utils.color import Color
from utils.objects.general_object import GeneralObject


class Layer:
    serializable = ['name', 'hidden', 'color', 'thickness']

    def __init__(self, name='', hidden=False, color: Color = None, thickness=2):
        self.hidden = hidden
        self.color = color
        self.thickness = thickness
        self.objects = []
        self.name = name

    def __getitem__(self, item):
        return self.objects[item]

    def add_object(self, general_object):
        self.objects.append(general_object)

    def add_object_from_dict(self, dct):
        self.objects.append(GeneralObject.from_dict(dct))

    def delete_object(self, index):
        self.objects.pop(index)

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def draw_qt(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw_qt()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        self.objects = []

    def move_objects(self, x, y):
        for obj in self.objects:
            obj.move(x, y)

    def to_dict(self):
        return {'name': self.name, 'hidden': self.hidden, 'color': self.color, 'thickness': self.thickness,
                'objects': [obj.to_dict(True) for obj in self.objects]}

    @staticmethod
    def from_dict(dct: dict):
        """
        Function that creates layer from the given dictionary.
        :param dct: dictionary
        :return: layer
        """

        # Checking if it is possible to create a layer
        for field in Layer.serializable:
            if field not in dct:
                raise ValueError(f'Unable to create layer, no such field in the given dictionary: {field}.')

        # Creating layer
        layer = Layer(*(dct[field] for field in Layer.serializable))
        layer.objects = list()
        if 'objects' in dct:
            for object_dict in dct['objects']:
                try:
                    layer.objects.append(GeneralObject.from_dict(object_dict))
                except ValueError as e:
                    print(e)

        return layer

    @staticmethod
    def empty():
        return Layer("Layer 1")

    def set_name(self, name):
        self.name = name

    def set_hidden(self, hidden):
        self.hidden = hidden
        if hidden:
            for el in self.objects:
                el.hide_name_bars()
        else:
            for el in self.objects:
                el.show_name_bars()

    def replace_object(self, index, dct):
        self.objects[index].destroy_name_bars()
        self.objects[index] = GeneralObject.from_dict(dct)
