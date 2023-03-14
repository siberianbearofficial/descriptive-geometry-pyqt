from utils.objects.general_object import GeneralObject


class Layer:
    def __init__(self, name='', hidden=False, color=None, thickness=2):
        self.hidden = hidden
        self.color = color
        self.thickness = thickness
        self.objects = []
        self.name = name

        self.serializable = ['hidden', 'objects', 'name']

    def add_object(self, general_object):
        self.objects.append(general_object)

    def add_object_from_dict(self, dct):
        self.objects.append(GeneralObject.from_dict(dct))
        # self.plot.sm.update_intersections()

    def delete_object(self, index, history_record=True):
        # if history_record:
        #     self.plot.hm.add_record('delete_object', self.objects[-1].to_dict())
        self.objects[index].delete()
        self.objects.pop(index)
        # self.plot.sm.update_intersections()

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
        for obj in self.objects:
            obj.destroy_name_bars()
        self.objects = []

    def move_objects(self, x, y):
        for obj in self.objects:
            obj.move(x, y)

    def to_dict(self):
        return {'name': self.name, 'hidden': self.hidden, 'objects': [obj.to_dict(True) for obj in self.objects]}

    @staticmethod
    def from_dict(dct, plot):
        layer = Layer(plot, dct['name'], dct['hidden'])
        layer.objects = [GeneralObject.from_dict(el) for el in dct['objects']]
        return layer

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
        # self.plot.update()

    def replace_object(self, index, dct):
        self.objects[index].destroy_name_bars()
        self.objects[index] = GeneralObject.from_dict(dct)
        # self.plot.sm.update_intersections()