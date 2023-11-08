import random
from uuid import UUID

from PyQt6.QtCore import pyqtSignal, QObject

from utils.color import *
from utils.history.history_manager import HistoryManager
from utils.objects.general_object import GeneralObject
from utils.objects.layer import Layer


class ObjectManager(QObject):
    objectAdded = pyqtSignal(GeneralObject)
    objectDeleted = pyqtSignal(UUID)
    objectSelected = pyqtSignal(object)
    objectColorChanged = pyqtSignal(UUID)
    objectAgChanged = pyqtSignal(UUID)
    objectRenamed = pyqtSignal(UUID)

    layerAdded = pyqtSignal(Layer)
    layerDeleted = pyqtSignal(UUID)
    layerSelected = pyqtSignal(UUID)
    layerColorChanged = pyqtSignal(UUID)
    layerNameChanged = pyqtSignal(UUID)
    layerHiddenChanged = pyqtSignal(UUID)

    def __init__(self, tm):
        super().__init__()
        self.theme_manager = tm
        self.objects = dict()
        self.selected_object = None

        layer = Layer.empty()
        self.layers = {layer.id: layer}
        self.current_layer = layer.id

        self.hm = HistoryManager(self)

    def new_object(self, ag_object, layer_id=None):
        name = ''
        if layer_id is None:
            layer_id = self.current_layer
        layer = self.layers[layer_id]
        if layer.color.type == ObjectColor.RANDOM:
            color = random.choice(STD_COLORS)
        else:
            color = layer.color
        obj = GeneralObject(ag_object, layer_id, color, name)
        self.objects[obj.id] = obj
        self.objectAdded.emit(obj)

    def add_object_from_dict(self, dct, history_record=True):
        if history_record:
            self.hm.add_record('add_object', index=(self.current_layer, len(self.layers[self.current_layer].objects)))
        obj = GeneralObject.from_dict(dct)
        self.layers[self.current_layer].add_object(obj)
        self.objectAdded.emit(obj)
        if self.objects_changed:
            self.objects_changed(self.layers[self.current_layer])

    def delete_object(self, obj_id=None, history_record=True):
        if obj_id is None:
            obj_id = self.selected_object
        if not isinstance(obj_id, UUID):
            return
        obj = self.get_object(obj_id)

        # if history_record:
        #     self.hm.add_record('delete_object', dict=obj.to_dict(), index=obj_id)
        self.objects.pop(obj_id)
        self.objectDeleted.emit(obj_id)
        if obj_id == self.selected_object:
            self.select_object(None)

    def add_layer(self, name=None, index=None, hidden=False, dct=None, history_record=True):
        if not name and not dct:
            name = Layer.generate_name(self.layers)
        if history_record:
            self.hm.add_record('add_layer', index=(len(self.layers) if index is None else index))
        if index is None:
            self.layers.append(Layer.from_dict(dct) if dct else Layer(name, hidden))
        else:
            self.layers.insert(index, Layer.from_dict(dct) if dct else Layer(name, hidden))
        for func in self.func_layer_add:
            func(self.layers[-1] if index is None else self[index], (len(self.layers) - 1 if index is None else index))

    def new_layer(self):
        layer = Layer.empty()
        self.layers[layer.id] = layer
        self.layerAdded.emit(layer)

    def select_layer(self, layer_id, history_record=True):
        if history_record:
            self.hm.add_record('select_layer', layer=self.current_layer)
        self.current_layer = layer_id
        self.layerSelected.emit(layer_id)

    def select_object(self, _id):
        self.selected_object = _id
        self.objectSelected.emit(_id)

    def set_layer_hidden(self, layer_id, hidden, history_record=True):
        if history_record:
            self.hm.add_record('layer_hidden', index=layer_id, hidden=self.layers[layer_id].hidden)
        self.layers[layer_id].hidden = hidden
        self.layerHiddenChanged.emit(layer_id)

    def delete_layer(self, layer_id, history_record=True):
        if layer_id == self.current_layer:
            return
        if history_record:
            self.hm.add_record('delete_layer', dict=self.layers[layer_id].to_dict(), index=layer_id)
        self.layers.pop(layer_id)
        self.layerDeleted.emit(layer_id)

    def get_all_objects(self):
        """
        Yields all non-hidden objects.
        :return: objects
        """
        for obj in self.objects.values():
            if not self.layers[obj.layer_id].hidden:
                yield obj

    def get_object(self, obj_id):
        return self.objects[obj_id]

    def get_layer(self, layer_id):
        return self.layers[layer_id]

    def get_object_color(self, obj_id):
        obj = self.objects[obj_id]
        if obj.color.type == ObjectColor.STANDARD:
            return self.theme_manager['Colors'][obj.color.color]
        if obj.color.type == ObjectColor.FROM_LAYER:
            return self.theme_manager['Colors'][self.layers[obj.layer_id].color.color]

    def set_layer_color(self, color, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if history_record:
            self.hm.add_record('layer_color', index=layer, color=self.layers[layer].color)
        self.layers[layer].color = color
        self.layerColorChanged.emit(layer)

    def set_layer_attr(self, attr_name, attr, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if self[layer].__dict__.get(attr_name, None) == attr:
            return
        if history_record:
            self.hm.add_record(f'layer_{attr_name}', index=layer, name=self[layer].__dict__.get(attr_name, None))
        self[layer].__dict__[attr_name] = attr
        for func in self.funcs_layer[attr_name]:
            func(layer, attr)

    def set_layer_name(self, name, layer=None, history_record=True):
        if layer is None:
            layer = self.current_layer
        if history_record:
            self.hm.add_record('layer_name', index=layer, name=self.layers[layer].name)
        self.layers[layer].name = name
        self.layerNameChanged.emit(layer)

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
        obj = self.get_object(index)
        if history_record:
            self.hm.add_record('set_obj_name', name=obj.name, index=index)
        obj.set_name(name)
        self.objectRenamed.emit(obj.id)

    def set_object_color(self, color: ObjectColor, obj_id=None, history_record=True):
        if obj_id is None:
            obj_id = self.selected_object
        obj = self.get_object(obj_id)
        if color.type == ObjectColor.FROM_LAYER and self.layers[obj.layer_id].color.type == ObjectColor.RANDOM:
            color = random.choice(STD_COLORS)
        if history_record:
            self.hm.add_record('set_obj_color', color=obj.color, index=obj_id)
        obj.set_color(color)
        self.objectColorChanged.emit(obj_id)

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

    def set_object_ag_obj(self, dct, obj_id=None, history_record=True):
        if obj_id is None:
            obj_id = self.selected_object
        # if history_record:
        #     self.hm.add_record('set_obj_ag_object', dct=self[index].thickness, index=index)
        obj = self.get_object(obj_id)
        obj.set_ag_object(dct)
        self.objectAgChanged.emit(obj_id)

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

    def serialize(self):
        ready = {'current_layer': self.current_layer, 'layers': [layer.to_dict() for layer in self.layers]}
        return ready

    def clear(self):
        self.select_object(0)
        self.layers.clear()
        self.layers.append(Layer.empty())
        self.plot_full_update(self.get_all_objects())
        if self.func_layers_clear:
            self.func_layers_clear(self.layers, self.current_layer)
        if self.objects_changed:
            self.objects_changed(self.layers[self.current_layer])

    def deserialize(self, dct: dict) -> None:
        """
        Function that unpacks and applies given dictionary.
        :param dct: dictionary
        :return:
        """

        self.clear()

        # Checking if it is possible to unpack layers
        for field in ('layers', 'current_layer'):
            if field not in dct:
                raise ValueError(f'Invalid dictionary, no such field: {field}.')

        # Unpacking layers
        self.layers.clear()
        for layer_dict in dct['layers']:
            try:
                layer = Layer.from_dict(layer_dict)
                self.layers.append(layer)
            except ValueError as e:
                print('Exception in ObjectManager (deserialize func):', e)
        if not self.layers:
            self.layers.append(Layer.empty())

        self.set_current_layer(dct['current_layer'])
        self.plot_full_update(self.get_all_objects())

        # Notifying all managers that objects have changed
        if self.objects_changed:
            self.objects_changed(self.layers[self.current_layer])

    def set_current_layer(self, index) -> None:
        """
        Function that sets current layer's index.
        :param index: index of the current layer
        :return:
        """

        if isinstance(index, int):
            self.current_layer = min(len(self.layers), max(0, index))
        else:
            try:
                self.set_current_layer(int(index))
            except TypeError:
                self.current_layer = 0
