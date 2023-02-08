import utils.maths.angem as ag

angem_objects = {
    ag.Point: ['x', 'y', 'z'],
    ag.Vector: ['x', 'y', 'z'],
    ag.Line: ['point', 'vector'],
    ag.Plane: ['normal', 'point'],
    ag.Segment: ['p1', 'p2'],
    ag.Circle: ['center', 'radius', 'normal'],
    ag.Arc: ['p1', 'p2', 'center', 'big_arc'],
    ag.Ellipse: [],
    ag.Sphere: ['center', 'radius'],
    ag.Cylinder: ['center1', 'center2', 'radius'],
    ag.Cone: ['center1', 'center2', 'radius1', 'radius2'],
    ag.Tor: ['center', 'radius', 'tube_radius', 'vector'],
    ag.Spline: ['plane', 'points'],
    ag.Spline3D: ['points'],
    ag.RotationSurface: ['center1', 'center2', 'spline1'],
}

angem_class_by_name = {key.__name__: key for key in angem_objects}
