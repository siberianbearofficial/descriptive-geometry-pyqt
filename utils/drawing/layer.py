from utils.drawing.general_object import GeneralObject


class Layer:
    def __init__(self, plot, hidden=False):
        self.plot = plot
        self.hidden = hidden
        self.objects = []

    def add_object(self, ag_object, color):
        self.objects.append(GeneralObject(self.plot, ag_object, color))

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        self.objects = []
