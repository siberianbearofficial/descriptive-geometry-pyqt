from PyQt5.QtWidgets import QMenuBar, QAction


class MenuBar(QMenuBar):
    def __init__(self, struct, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        _, self.action_dict = self.unpack(struct)

    def unpack(self, struct, parent=None, name=None):
        if not isinstance(struct, dict):
            return self.action(name, *struct), None

        if parent:
            menu = parent.addMenu(f'&{name}')
        else:
            menu = self

        dct = dict()
        for name in struct:
            got, d = self.unpack(struct[name], menu, name)
            if isinstance(got, QAction):
                menu.addAction(got)
                dct[name] = got
            else:
                menu.addMenu(got)
                dct[name] = d
        return menu, dct

    def action(self, name, func=None, shortcut=None):
        action = QAction(f'&{name}', self)
        if func:
            action.triggered.connect(func)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def set_styles(self):
        self.setStyleSheet(self.theme_manager.get_style_sheet(self.__class__.__name__))

