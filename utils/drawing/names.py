import core.angem as ag


used_points = []
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
        return get_alpha(lower=True)
    return 'GENERATE'


def get_alpha(lower=False):
    if lower:
        for symbol in alph:
            if symbol not in used_points:
                used_points.append(symbol)
                return symbol
        i, s = 1, '1'
        while True:
            for symbol in alph:
                if symbol + s not in used_points:
                    used_points.append(symbol + s)
                    return symbol + s
            i += 1
            s = str(i)
    else:
        for symbol in ALPH:
            if symbol not in used_points:
                used_points.append(symbol)
                return symbol
        i, s = 1, '1'
        while True:
            for symbol in ALPH:
                if symbol + s not in used_points:
                    used_points.append(symbol + s)
                    return symbol + s
            i += 1
            s = str(i)


def projections(plot, ag_object, config):
    proj = plot.pm.get_projection(ag_object, (0, 0, 0), **config)
    xy_projection, xz_projection = proj[0], proj[1]
    connection_lines = proj[2] if len(proj) >= 3 else tuple()
    if not isinstance(xy_projection, (tuple, list)):
        xy_projection = xy_projection,
    if not isinstance(xz_projection, (tuple, list)):
        xz_projection = xz_projection,
    if not isinstance(connection_lines, (tuple, list)):
        connection_lines = connection_lines,
    return xy_projection, xz_projection, connection_lines


def name_to_point(plot, pos):
    name = plot.lm.get_name_to_new_obj(pos)
    if name:
        return name
    return get_alpha()

