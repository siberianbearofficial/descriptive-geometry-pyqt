from utils.drawing.general_object import GeneralObject
import utils.maths.angem as ag


class Layer:
    def __init__(self, plot, name='', hidden=False):
        self.plot = plot
        self.hidden = hidden
        self.objects = []
        self.name = name

        self.serializable = ['hidden', 'objects']

    def add_object(self, ag_object, color):
        self.objects.append(GeneralObject(self.plot, ag_object, color))
        self.plot.sm.update_intersections()

    def delete_object(self, index):
        self.objects.pop(index)
        self.plot.sm.update_intersections()
        self.plot.full_update()

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        self.objects = []
