import json

from utils.drawing.screen import Screen
from utils.drawing.layer import Layer
from utils.drawing.plot import Plot
from utils.drawing.general_object import GeneralObject
from utils.drawing.command_line import CommandLine
from utils.drawing.toolbar import Toolbar2

from utils.history.serializable import angem_objects, angem_class_by_name


def serialize(screen, path='history.txt'):
    """
    Function to serialize screen history to file.
    :param screen: screen to serialize
    :param path: path to the history file
    """

    class Serializer(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Plot) or isinstance(obj, Layer) or isinstance(obj, Screen):
                to_serialize = dict()
                for field_name in obj.serializable:
                    to_serialize[field_name] = obj.__dict__.get(field_name, '')
                return to_serialize
            elif isinstance(obj, GeneralObject):
                return {'ag_object': obj.ag_object, 'color': obj.color}
            elif isinstance(obj, CommandLine) or isinstance(obj, Toolbar2):
                return ''
            return try_serialize(obj)

    def try_serialize(obj):
        for key in angem_objects:
            if isinstance(obj, key):
                return serialize_object(obj)
        try:
            return {'__{}__'.format(obj.__class__.__name__): obj.__dict__}
        except AttributeError:
            return str(obj)

    def serialize_object(obj):
        to_serialize = {'name': obj.__class__.__name__}
        for field_name in angem_objects[obj.__class__]:
            to_serialize[field_name] = obj.__dict__.get(field_name, '')
        return to_serialize

    hist = json.dumps(screen, cls=Serializer, indent=2)  # TODO: remove indent to save disk space
    print(hist, file=open(path, 'w', encoding='utf-8'), end='')


def deserialize(screen, path='history.txt'):
    """
    Function to deserialize history from file and apply it to the screen.
    :param screen: screen to draw on
    :param path: path to the history file
    """

    def deserialize_layers(layers_hist):
        layers = list()
        for layer_hist in layers_hist:
            layer = Layer(screen.plot, layer_hist['name'], layer_hist['hidden'])
            for obj_hist in layer_hist['objects']:
                obj = try_deserialize_ag_object(obj_hist['ag_object'])
                layer.add_object(obj, obj_hist['color'])
            layers.append(layer)
        return layers

    def try_deserialize_ag_object(serialized):
        if isinstance(serialized, dict) and 'name' not in serialized:
            return serialized.values()
        elif not isinstance(serialized, dict):
            return serialized
        object_class = angem_class_by_name.get(serialized['name'], None)
        if object_class:
            params = list()
            for key, val in serialized.items():
                if key != 'name':
                    params.append(try_deserialize_ag_object(val))

            show_exception = object_instance = None
            try:
                object_instance = object_class(*params)
            except ValueError as e:
                print('Serialized:', serialized)
                print('Params for instantiating last object:', *params)
                show_exception = e
            if show_exception is not None:
                raise AttributeError(
                    f'Exception occurred while instantiating object: {show_exception}.\nPossible reason: inaccurate '
                    f'class specification for {object_class.__name__}.\nCheck: {angem_objects[object_class]}.\n'
                    f'Also check the given file not to be broken or outdated.'
                )
            else:
                return object_instance
        else:
            raise AttributeError('Angem object undefined:', serialized['name'])

    hist = json.loads(open(path, encoding='utf-8').read())
    screen.update(hist['title'], hist['bg_color'])
    plot_hist = hist['plot']
    screen.plot.update(plot_hist['bg_color'], deserialize_layers(plot_hist['layers']))
