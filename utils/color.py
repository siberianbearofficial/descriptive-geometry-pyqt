from PyQt5.QtGui import QColor

from random import randint


class Color(QColor):
    def __init__(self, red, green=None, blue=None, alpha=None):
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
                    color.append(min(int(float(''.join(new_col))), 255))
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
            raise ValueError('Oops, invalid color format!')

    def __str__(self):
        return f'rgba({self.red()}, {self.green()}, {self.blue()}, {self.alpha()})'

    @staticmethod
    def random():
        red = randint(20, 240)
        green = randint(20, 240)
        blue = randint(20, min(570 - red - green, 240))
        return Color(red, green, blue)


ACCENT_COLOR = Color('#00ABB3')
DARK_COLOR = Color('#3C4048')
LIGHT_COLOR = Color('#EAEAEA')
WHITE_COLOR = Color('#FFFFFF')
BLACK_COLOR = Color('#000000')
CONNECT_LINE_COLOR = Color(180, 180, 180)
DRAW_COLOR = Color(0, 162, 232)
SELECTION_COLOR = Color(250, 30, 30)

if __name__ == '__main__':
    a = Color('#f8a2bb')
    b = Color(18, 25, 10)
    c = Color(35, 26, 152, 199)
    d = Color('241, 45, 14')
    e = Color('32, 87, 188, 187')
    f = Color('rgba(222, 182, 99)')
    g = Color('rgba(77, 188, 166, 155)')
    print(a, b, c, d, e, f, g, sep='\n')
