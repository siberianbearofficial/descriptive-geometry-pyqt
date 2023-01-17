import json
import utils.maths.angem as ag

from utils.drawing.screen import Screen
from utils.drawing.layer import Layer
from utils.drawing.plot import Plot
from utils.drawing.general_object import GeneralObject
from utils.drawing.command_line import CommandLine
from utils.drawing.toolbar import Toolbar2


def serialize(screen):
    """
    Function to serialize screen history to file.
    :param screen: screen to serialize
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

            try:
                return {'__{}__'.format(obj.__class__.__name__): obj.__dict__}
            except AttributeError:
                return str(obj)

    hist = json.dumps(screen, cls=Serializer)
    print(hist, file=open('history.txt', 'w', encoding='utf-8'), end='')


def deserialize(screen):
    """
    Function to deserialize history from file and apply it to the screen.
    :param screen: screen to draw on
    """

    def deserialize_layers(layers_hist):
        layers = list()
        for layer_hist in layers_hist:
            layer = Layer(screen.plot, layer_hist['hidden'])
            for obj_hist in layer_hist['objects']:
                obj = deserialize_ag_object(obj_hist['ag_object'])
                layer.add_object(obj, obj_hist['color'])
            layers.append(layer)
        return layers

    def deserialize_ag_object(hist):
        if '__Point__' in hist:
            ag_hist = hist['__Point__']
            return ag.Point(ag_hist['x'], ag_hist['y'], ag_hist['z'])
        elif '__Segment__' in hist:
            ag_hist = hist['__Segment__']
            return ag.Segment(deserialize_ag_object(ag_hist['p1']),
                              deserialize_ag_object(ag_hist['p2']))
        elif '__Circle__' in hist:
            ag_hist = hist['__Circle__']
            return ag.Circle(deserialize_ag_object(ag_hist['center']), ag_hist['radius'])
        else:
            raise ValueError('Unknown ag_object type: ' + str(hist))

    hist = json.loads(open('history.txt', encoding='utf-8').read())
    screen.update(hist['title'], hist['bg_color'])
    plot_hist = hist['plot']
    screen.plot.update(plot_hist['bg_color'], deserialize_layers(plot_hist['layers']))
