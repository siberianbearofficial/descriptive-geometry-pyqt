import math

from core.matrix import Matrix
import core.angem as ag


def distance(object1, object2):
    """
    Вычисляет расстояние между двумя объектами
    :param object1: точка, прямая или плоскость
    :param object2: точка, прямая или плоскость
    :return: float
    """
    if isinstance(object1, ag.Point) and isinstance(object2, ag.Point):
        return abs(ag.Vector(object1, object2))
    if isinstance(object1, ag.Point) and isinstance(object2, ag.Plane):
        return abs(object1.x * object2.normal.x + object1.y * object2.normal.y + object1.z * object2.normal.z +
                   object2.d) / abs(object2.normal)
    if isinstance(object1, ag.Plane) and isinstance(object2, ag.Point):
        return abs(object2.x * object1.normal.x + object2.y * object1.normal.y + object2.z * object1.normal.z +
                   object1.d) / abs(object1.normal)
    if isinstance(object1, ag.Point) and isinstance(object2, ag.Line):
        return (((object1.y - object2.point.y) * object2.vector.z - (
                    object1.z - object2.point.z) * object2.vector.y) ** 2
                + ((object1.x - object2.point.x) * object2.vector.z - (object1.z - object2.point.z) *
                   object2.vector.x) ** 2
                + ((object1.x - object2.point.x) * object2.vector.y - (object1.y - object2.point.y) *
                   object2.vector.x) ** 2) \
               ** 0.5 / abs(object2.vector)
    if isinstance(object1, ag.Line) and isinstance(object2, ag.Point):
        return (((object2.y - object1.point.y) * object1.vector.z - (object2.z - object1.point.z) * object1.vector.y) +
                ((object2.x - object1.point.x) * object1.vector.z - (object2.z - object1.point.z) * object1.vector.x) +
                ((object2.x - object1.point.x) * object1.vector.y - (object2.y - object1.point.y) * object1.vector.x)) \
               ** 0.5 / abs(object1.vector)
    if isinstance(object1, ag.Line) and isinstance(object2, ag.Line):
        return abs(Matrix([[object2.point.x - object1.point.x, object2.point.y - object1.point.y,
                            object2.point.z - object1.point.z],
                          [object1.vector.x, object1.vector.y, object1.vector.z],
                          [object2.vector.x, object2.vector.y, object2.vector.z]]).determinant()) / (
                       (object2.vector.y * object1.vector.z - object2.vector.z * object1.vector.y) ** 2 +
                       (object2.vector.x * object1.vector.z - object2.vector.z * object1.vector.x) ** 2 +
                       (object2.vector.x * object1.vector.y - object2.vector.y * object1.vector.x) ** 2) ** 0.5
    raise ValueError(f'unsupported operand types:  "{object1.__class__.__name__}" and "{object2.__class__.__name__}"')


def angle(object1, object2):
    """
    Вычисляет угол между двумя объектами (в радианах)
    :param object1: вектор, прямая или плоскость
    :param object2: вектор, прямая или плоскость
    :return: float
    """
    flag = False
    if isinstance(object1, ag.Vector):
        vector1 = object1
    elif isinstance(object1, ag.Line):
        vector1 = object1.vector
    elif isinstance(object1, ag.Plane):
        vector1 = object1.normal
        flag = True
    else:
        raise ValueError
    if isinstance(object2, ag.Vector):
        vector2 = object2
    elif isinstance(object2, ag.Line):
        vector2 = object2.vector
    elif isinstance(object2, ag.Plane):
        vector2 = object2.normal
        flag = True
    else:
        raise ValueError(f'unsupported operand types:  "{object1.__class__.__name__}"'
                         f'and "{object2.__class__.__name__}"')
    if flag:
        return math.asin(vector1 * vector2 / (abs(vector1) * abs(vector2)))
    cos = vector1 * vector2 / (abs(vector1) * abs(vector2))
    if abs(cos) >= 1:
        return 0
    return math.acos(vector1 * vector2 / (abs(vector1) * abs(vector2)))
