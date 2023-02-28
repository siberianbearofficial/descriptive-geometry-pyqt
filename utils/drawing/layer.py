from utils.drawing.general_object import GeneralObject


class Layer:
    def __init__(self, plot, name='', hidden=False):
        self.plot = plot
        self.hidden = hidden
        self.objects = []
        self.name = name

        self.serializable = ['hidden', 'objects', 'name']

    def add_object(self, ag_object, color, history_record=True):
        self.objects.append(GeneralObject(self.plot, ag_object, color, name='GENERATE'))
        self.plot.sm.update_intersections()
        if history_record:
            self.plot.hm.add_record('add_object', ag_object, color)
    def delete_object(self, index, history_record=True):
        if history_record:
            self.plot.hm.add_record('delete_object', self.objects[-1].ag_object, self.objects[-1].color)
        self.objects.pop(index)
        self.plot.sm.update_intersections()

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
