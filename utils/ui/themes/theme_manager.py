from utils.color import *
from utils.ui.styles.cmd_bar_css import style_sheet as cmd_bar_css
from utils.ui.styles.draw_bar_css import style_sheet as draw_bar_css
from utils.ui.styles.inspector_bar_css import style_sheet as inspector_bar_css
from utils.ui.styles.plot_bar_css import style_sheet as plot_bar_css
from utils.ui.styles.properties_bar_css import style_sheet as properties_bar_css
from utils.ui.styles.toolbar_css import style_sheet as toolbar_css
from utils.ui.styles.main_window_css import style_sheet as main_window_css
from utils.ui.styles.memu_bar_css import style_sheet as menu_bar_css


PARENT = 0
COLOR = 1


class ThemeManager:
    style_sheets = {
        'CmdBar': cmd_bar_css,
        'DrawBar': draw_bar_css,
        'InspectorBar': inspector_bar_css,
        'PlotBar': plot_bar_css,
        'PropertiesBar': properties_bar_css,
        'ToolBar': toolbar_css,
        'MainWindow': main_window_css,
        'MenuBar': menu_bar_css,
    }

    basic_theme = {
        '__name__': 'Basic',
        '__general__': {
            'LIGHT_COLOR': LIGHT_COLOR,
            'ACCENT_COLOR': ACCENT_COLOR,
            'DARK_COLOR': DARK_COLOR,
            'WHITE_COLOR': WHITE_COLOR,
            'BLACK_COLOR': BLACK_COLOR,
            'CONNECT_LINE_COLOR': CONNECT_LINE_COLOR,
            'DRAW_COLOR': DRAW_COLOR,
            'SELECTION_COLOR': SELECTION_COLOR,
            'BORDER_RADIUS': '10px'
        },
        'CmdBar': {
            'background-color': (COLOR, '#B2B2B2'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'DrawBar': {
            'background-color': (PARENT, 'LIGHT_COLOR'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'InspectorBar': {
            'background-color': (PARENT, 'LIGHT_COLOR'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'PlotBar': {
            'background-color': (PARENT, 'LIGHT_COLOR'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'PropertiesBar': {
            'background-color': (PARENT, 'LIGHT_COLOR'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'ToolBar': {
            'background-color': (PARENT, 'LIGHT_COLOR'),
            'border-radius': (PARENT, 'BORDER_RADIUS')
        },
        'MainWindow': {
            'background-color': (PARENT, 'DARK_COLOR')
        },
        'MenuBar': {
            'color': (PARENT, 'BLACK_COLOR'),
            'background-color': (PARENT, 'WHITE_COLOR'),
            'item:selected:background-color': (PARENT, 'LIGHT_COLOR')
        },
    }

    def __init__(self):
        self.theme = ThemeManager.basic_theme

    def get(self, *args):
        if len(args) == 1:
            return self.get('__general__', *args)

        r = self.theme.get(args[0], dict()).get(args[1], ThemeManager.basic_theme[args[0]][args[1]])
        if isinstance(r, tuple):
            t, v = r
            if t == PARENT:
                return self.get(v)
            if t == COLOR:
                return Color(v)
        return r

    def get_style_sheet(self, key):
        return self.style_sheets[key](key, self)

    def set_theme(self, theme):
        self.theme = theme

    def load_theme(self, name):
        pass
