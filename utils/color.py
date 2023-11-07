import random

from PyQt6.QtGui import QColor

from random import randint


class Color(QColor):
    def __init__(self, red, green=None, blue=None, alpha=None):
        if isinstance(red, (tuple, list)):
            if len(red) == 3:
                red, green, blue = red
            elif len(red) == 4:
                red, green, blue, alpha = red
            else:
                raise ValueError('Oops, invalid color format!')
        if isinstance(red, str):
            if '#' in red:
                super().__init__(red.strip())
            else:
                color = list()
                for col in red.strip().split():
                    new_col = list()
                    for el in col:
                        if el.isdigit() or el in '.,':
                            new_col.append(el.replace(',', '.'))
                    if new_col_str := ''.join(new_col):
                        color.append(min(int(float(new_col_str)), 255))
                    else:
                        raise ValueError(f'Oops, invalid color format: {red}, {green}, {blue}, {alpha}!')
                super().__init__(*color)
        elif red is not None and green is not None and blue is not None:
            red, green, blue = int(float(red)), int(float(green)), int(float(blue))
            if alpha:
                super().__init__(red, green, blue, alpha)
            else:
                super().__init__(red, green, blue)
        elif isinstance(red, QColor):
            super().__init__(red)
        else:
            raise ValueError(f'Oops, invalid color format: {red}, {green}, {blue}, {alpha}!')

    @staticmethod
    def valid(color_str: str):
        try:
            Color(color_str)
            return True
        except ValueError:
            return False

    def __str__(self):
        return self.name()

    @staticmethod
    def random():
        red = randint(20, 240)
        green = randint(20, 240)
        blue = randint(20, min(570 - red - green, 240))
        return Color(red, green, blue)


class ObjectColor:
    RANDOM = 1
    FROM_LAYER = 2
    STANDARD = 3
    OTHER = 4

    def __init__(self, color, color_type=4):
        self.type = color_type
        self.color = color


LAYER_COLOR = ObjectColor(None, ObjectColor.FROM_LAYER)
RANDOM_COLOR = ObjectColor(None, ObjectColor.RANDOM)
STD_COLORS = [ObjectColor(i, ObjectColor.STANDARD) for i in range(12)]

