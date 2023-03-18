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
        self.last_selected_object_index = None
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
        if history_record:
            self.hm.add_record('add_object', index=(self.current_layer, len(self.layers[self.current_layer].objects)))
        obj = GeneralObject(ag_object, color, name, **config)
        self.layers[self.current_layer].add_object(obj)
        self.func_plot_obj(obj.id, obj)
        self.func_plot_update()

    def add_object_from_dict(self, dct, history_record=True):
        if history_record:
            self.hm.add_record('add_object', index=(self.current_layer, len(self.layers[self.current_layer].objects)))
        obj = GeneralObject.from_dict(dct)
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
            self.hm.add_record('delete_object', dict=self.selected_object.to_dict(), index=self.selected_object_index)
        if self.selected_object is None:
            return
        self.layers[self.selected_object_index[0]].delete_object(
            self.selected_object_index[1])
        self.func_plot_obj(self.selected_object.id, None)
        self.selected_object = None
        for func in self.func_object_selected:
            func(0)
        self.func_plot_update()

    def delete_object(self, layer, index, history_record=True):
        obj = self.layers[layer].objects[index]
        if history_record:
            self.hm.add_record('delete_object', dict=obj.to_dict(), index=(layer, index))
        self.layers[layer].delete_object(index)
        self.func_plot_obj(obj.id, None)
        if (layer, index) == self.selected_object_index:
            self.selected_object_index = None
        for func in self.func_object_selected:
            func(0)
        self.func_plot_update()

    def add_layer(self, name=None, index=None, hidden=False, dct=None, history_record=True):
        if not name and not dct:
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
            self.hm.add_record('add_layer', index=(len(self.layers) if index is None else index))
        if index is None:
            self.layers.append(Layer.from_dict(dct) if dct else Layer(name, hidden))
        else:
            self.layers.insert(index, Layer.from_dict(dct) if dct else Layer(name, hidden))
        for func in self.func_layer_add:
            func(self.layers[-1] if index is None else self[index], (len(self.layers) - 1 if index is None else index))

    def select_layer(self, index, history_record=True):
        if history_record:
            self.hm.add_record('select_layer', layer=self.current_layer)
        if 0 <= index < len(self.layers):
            self.current_layer = index
        for func in self.func_layer_select:
            func(index)

    def select_object(self, id):
        self.last_selected_object_index = self.selected_object_index
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
        if self[ind].hidden == hidden:
            return
        if history_record:
            self.hm.add_record('layer_hidden', index=ind, hidden=self[ind].hidden)
        self.layers[ind].hidden = hidden
        self.plot_full_update(self.get_all_objects())

    def delete_layer(self, index, history_record=True):
        if index == self.current_layer:
            return
        if history_record:
            self.hm.add_record('delete_layer', dict=self.layers[index].to_dict(), index=index)
        self.layers.pop(index)
        if self.current_layer >= index:
            self.current_layer -= 1
        for func in self.func_layer_delete:
            func(index)
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

    def set_layer_color(self, color, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if self[layer].color == color:
            return
        if history_record:
            self.hm.add_record('layer_color', index=layer, color=self[layer].color)
        self.layers[layer].color = color
        for func in self.func_layer_color:
            func(layer, color)

    def set_layer_name(self, name, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if self[layer].name == name:
            return
        if history_record:
            self.hm.add_record('layer_name', index=layer, name=self[layer].name)
        self.layers[layer].name = name
        for func in self.func_layer_rename:
            func(layer, name)

    def set_layer_thickness(self, thickness, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if self[layer].thickness == thickness:
            return
        if history_record:
            self.hm.add_record('layer_thickness', index=layer, thickness=self[layer].thickness)
        self.layers[layer].thickness = thickness
        for func in self.func_layer_thickness:
            func(layer, thickness)

    def set_object_name(self, name, index=None, history_record=True):
        if index is None:
            index = self.selected_object_index or self.last_selected_object_index
        if self[index].name == name:
            return
        if history_record:
            self.hm.add_record('set_obj_name', name=self[index].name, index=index)
        obj = self[index]
        obj.set_name(name)
        self.func_plot_obj(obj.id, obj)

    def set_object_color(self, color, index=None, history_record=True):
        if index is None:
            index = self.selected_object_index or self.last_selected_object_index
        if self[index].color == color:
            return
        if history_record:
            self.hm.add_record('set_obj_color', color=self[index].color, index=index)
        obj = self[index]
        obj.set_color(color)
        self.func_plot_obj(obj.id, obj)

    def set_object_thickness(self, thickness, index=None, history_record=True):
        if index is None:
            index = self.selected_object_index or self.last_selected_object_index
        if self[index].thickness == thickness:
            return
        if history_record:
            self.hm.add_record('set_obj_thickness', thickness=self[index].thickness, index=index)
        obj = self[index]
        obj.set_thickness(thickness)
        self.func_plot_obj(obj.id, obj)

    def set_object_ag_obj(self, dct, index=None, history_record=True):
        if index is None:
            index = self.selected_object_index or self.last_selected_object_index
        if self[index].to_dict()['ag_object'] == dct:
            return
        if history_record:
            self.hm.add_record('set_obj_ag_object', dct=self[index].thickness, index=index)
        obj = self[index]
        obj.set_ag_object(dct)
        self.func_plot_obj(obj.id, obj)

    def set_object_config(self, config, index=None, history_record=True):
        if index is None:
            index = self.selected_object_index or self.last_selected_object_index
        if self[index].config == config:
            return
        if history_record:
            self.hm.add_record('set_obj_config', dct=self[index].config, index=index)
        obj = self[index]
        obj.set_config(config)
        self.func_plot_obj(obj.id, obj)

    def set_object_layer(self, new_layer, index=None, history_record=True):
        if index is None:
            if self.selected_object_index:
                index = self.selected_object_index
                obj = self.layers[index[0]].objects[index[1]]
                self.layers[index[0]].objects.remove(obj)
                self.layers[new_layer].add_object(obj)
                self.func_plot_obj(obj.id, obj)
                self.selected_object_index = new_layer, len(self.layers[new_layer].objects) - 1
            elif self.last_selected_object_index:
                index = self.last_selected_object_index
                obj = self.layers[index[0]].objects[index[1]]
                self.layers[index[0]].objects.remove(obj)
                self.layers[new_layer].add_object(obj)
                self.func_plot_obj(obj.id, obj)
                self.last_selected_object_index = new_layer, len(self.layers[new_layer].objects) - 1
        else:
            obj = self[index]
            self.layers[index[0]].objects.remove(obj)
            self.layers[new_layer].add_object(obj)
            if self.layers[new_layer].hidden:
                self.func_plot_obj(obj.id, None)
                if obj == self.selected_object:
                    self.selected_object_index = None
        if index is not None and history_record:
            self.hm.add_record('set_obj_layer', layer=index[0], index=(new_layer, len(self[new_layer].objects) - 1))

    def __getitem__(self, item):
        print(item)
        if isinstance(item, tuple):
            return self.layers[item[0]].objects[item[1]]
        return self.layers[item]

    def serialize(self):
        ready = {'current_layer': self.current_layer, 'layers': [layer.to_dict() for layer in self.layers]}
        return ready

    def clear(self):
        self.layers.clear()
        self.layers.append(Layer("Layer 1"))
        self.plot_full_update(self.get_all_objects())

    def deserialize(self, dct):
        self.layers.clear()
        for el in dct['layers']:
            self.layers.append(Layer.from_dict(el))
        self.current_layer = dct['current_layer']
        self.plot_full_update(self.get_all_objects())
