from PyQt5.QtWidgets import QMenuBar, QAction, QMenu


class MenuBar(QMenuBar):
    def __init__(self, struct):
        super().__init__()
        self.unpack(struct)

    def unpack(self, struct, parent=None, name=None):
        if not isinstance(struct, dict):
            return self.action(name, *struct)

        if parent:
            menu = parent.addMenu(f'&{name}')
        else:
            menu = self

        for name in struct:
            got = self.unpack(struct[name], menu, name)
            if isinstance(got, QAction):
                menu.addAction(got)
            else:
                menu.addMenu(got)

        return menu

    def action(self, name, func=None, shortcut=None):
        action = QAction(f'&{name}', self)
        if func:
            action.triggered.connect(func)
        if shortcut:
            action.setShortcut(shortcut)
        return action
