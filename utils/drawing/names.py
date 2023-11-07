import core.angem as ag


used_points = set()
SEP = '-'
ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alph = ALPH.lower()


def generate_name(plot, ag_object, config):
    proj = projections(plot, ag_object, config)
    xy_projection = proj[0]
    if isinstance(ag_object, ag.Point):
        return name_to_point(plot, xy_projection[0].tuple())
    elif isinstance(ag_object, ag.Segment):
        return name_to_point(plot, xy_projection[0].p1) + SEP + \
                    name_to_point(plot, xy_projection[0].p2)
    elif isinstance(ag_object, ag.Plane) and config.get('draw_3p', False):
        return name_to_point(plot, xy_projection[3].tuple()) + SEP + \
                    name_to_point(plot, xy_projection[4].tuple()) + SEP + \
                    name_to_point(plot, xy_projection[5].tuple())
    elif isinstance(ag_object, ag.Line) or isinstance(ag_object, ag.Plane):
        return '__lower__'
    return 'GENERATE'


def update_used_points(object_list):
    used_points.clear()
    for obj in object_list:
        ag_obj = obj.general_object.ag_object
        name = obj.general_object.name
        if isinstance(ag_obj, ag.Point):
            used_points.add(name)
        if isinstance(ag_obj, ag.Segment) and name.count(SEP) == 1:
            for el in name.split(SEP):
                used_points.add(el)
        if isinstance(ag_obj, ag.Plane) and obj.general_object.config.get('draw_3p', False) and name.count(SEP) == 1:
            for el in name.split(SEP):
                used_points.add(el)


def get_alpha(lower=False):
    if lower:
        for symbol in alph:
            if symbol not in used_points:
                used_points.add(symbol)
                return symbol
        i, s = 1, '1'
        while True:
            for symbol in alph:
                if symbol + s not in used_points:
                    used_points.add(symbol + s)
                    return symbol + s
            i += 1
            s = str(i)
    else:
        for symbol in ALPH:
            if symbol not in used_points:
                used_points.add(symbol)
                return symbol
        i, s = 1, '1'
        while True:
            for symbol in ALPH:
                if symbol + s not in used_points:
                    used_points.add(symbol + s)
                    return symbol + s
            i += 1
            s = str(i)


def name_to_point(plot, pos):
    name = plot.lm.get_name_to_new_obj(pos)
    if name:
        return name
    return '__UPPER__'

