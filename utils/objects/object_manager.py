from utils.objects.layer import Layer
from random import randint
from utils.objects.general_object import GeneralObject
from utils.history.history_manager import HistoryManager


class ObjectManager:
    def __init__(self, func_plot_update, func_plot_obj, plot_full_update, func_object_selected):
        self.layers = [Layer("Layer 1")]
        self.current_layer = 0
        self.selected_object = None
        self.selected_object_index = None
        self.func_plot_update = func_plot_update
        self.func_plot_obj = func_plot_obj
        self.plot_full_update = plot_full_update
        self.func_object_selected = func_object_selected
        self.hm = HistoryManager(self)

        self.func_layer_add = None
        self.func_layer_delete = None
        self.func_layer_hide = None
        self.func_layer_select = None
        self.func_layer_rename = None
        self.func_layer_color = None
        self.func_layer_thickness = None

    def set_layers_func(self, func_layer_add, func_layer_delete, func_layer_hide, func_layer_select, func_layer_rename,
                        func_layer_color, func_layer_thickness):
        self.func_layer_add = func_layer_add
        self.func_layer_delete = func_layer_delete
        self.func_layer_hide = func_layer_hide
        self.func_layer_select = func_layer_select
        self.func_layer_rename = func_layer_rename
        self.func_layer_color = func_layer_color
        self.func_layer_thickness = func_layer_thickness

    def add_object(self, ag_object, name='', color=None, history_record=True, **config):
        if color is None:
            color = self.random_color()
        obj = GeneralObject(ag_object, color, name, **config)
        self.layers[self.current_layer].add_object(obj)
        self.func_plot_obj(obj.id, obj)
        self.func_plot_update()

    def find_by_id(self, id):
        for i in range(len(self.layers)):
            for j in range(len(self.layers[i].objects)):
                if self.layers[i].objects[j].id == id:
                    return i, j

    def delete_selected_object(self, history_record=True):
        if history_record:
            self.hm.add_record('delete_object', self.selected_object.to_dict(), self.selected_object_index)
        if self.selected_object is None:
            return
        self.layers[self.selected_object_index[0]].delete_object(
            self.selected_object_index[1])
        self.func_plot_obj(self.selected_object.id, None)
        self.selected_object = None
        for func in self.func_object_selected:
            func(0)
        self.func_plot_update()

    def add_layer(self, name=None, hidden=False, history_record=True):
        if not name:
            i = 1
            while True:
                name = f'Layer {i}'
                for layer in self.layers:
                    if layer.name == name:
                        break
                else:
                    break
                i += 1
        if history_record:
            self.hm.add_record('add_layer', self.layers[-1].to_dict(), -1)
        self.layers.append(Layer(name, hidden))
        for func in self.func_layer_add:
            func(self.layers[-1])

    def select_layer(self, index):
        if 0 <= index < len(self.layers):
            self.current_layer = index
        for func in self.func_layer_select:
            func(index)

    def select_object(self, id):
        if id == 0:
            self.selected_object = None
            self.selected_object_index = None
            for func in self.func_object_selected:
                func(0)
        else:
            self.selected_object_index = self.find_by_id(id)
            self.selected_object = self.layers[self.selected_object_index[0]].objects[self.selected_object_index[1]]
            for func in self.func_object_selected:
                func(self.selected_object)

    def set_layer_hidden(self, ind, hidden, history_record=True):
        self.layers[ind].hidden = hidden
        self.plot_full_update(self.get_all_objects())

    def delete_layer(self, index, history_record=True):
        if index == self.current_layer:
            return
        if history_record:
            self.hm.add_record('delete_layer', self.layers[index].to_dict(), index)
        for func in self.func_layer_delete:
            func(index)
        self.layers.pop(index)
        if self.current_layer >= index:
            self.current_layer -= 1
        self.plot_full_update(self.get_all_objects())

    def get_all_objects(self):
        for layer in self.layers:
            if layer.hidden:
                continue
            for obj in layer.objects:
                yield obj

    @staticmethod
    def random_color():
        red = randint(20, 240)
        green = randint(20, 240)
        blue = randint(20, min(570 - red - green, 240))
        return red, green, blue
        while True:
            red = randint(20, 240)
            green = randint(20, 240)
            blue = randint(20, 570 - red - green)
            if 300 < red + green + blue < 570:
                return red, green, blue

    def set_layer_color(self, color, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].color = color
        for func in self.func_layer_color:
            func(layer, color)

    def set_layer_name(self, name, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].name = name
        for func in self.func_layer_rename:
            func(layer, name)

    def set_layer_thickness(self, thickness, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].thickness = thickness
        for func in self.func_layer_thickness:
            func(layer, thickness)

    def set_object_name(self, name, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].name = name

    def set_object_color(self, color, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].color = color

    def set_object_thickness(self, thickness, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].thickness = thickness

    def set_object_ag_obj(self, dct, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].ag_object = GeneralObject.from_dict(dct)

    def set_object_config(self, config, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].config = config

    def serialize(self):
        ready = {'current_layer': self.current_layer, 'layers': [layer.to_dict() for layer in self.layers]}
        # print(ready)
        return ready

    def clear(self):
        self.layers = [Layer("Layer 1")]
        self.plot_full_update(self.get_all_objects())

    def deserialize(self, dct):
        self.clear()
        self.layers = [Layer.from_dict(el, self) for el in dct['layers']]
        self.current_layer = dct['current_layer']
        self.plot_full_update(self.get_all_objects())
