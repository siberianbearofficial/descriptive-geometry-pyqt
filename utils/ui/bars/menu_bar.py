from PyQt5.QtWidgets import QMenuBar, QAction, QMenu


class MenuBar(QMenuBar):
    def __init__(self, menu_dict):
        super().__init__()

        for name in menu_dict:
            if not isinstance(menu_dict[name], dict):
                action = QAction('&{}'.format(name), self)
                action.triggered.connect(menu_dict[name][0])
                if menu_dict[name][1]:
                    action.setShortcut(menu_dict[name][1])
                self.addAction(action)
            else:
                menu = self.addMenu('&{}'.format(name))
                menu.addActions(self.unpack(menu_dict[name]))

    def unpack(self, data):
        actions = list()
        for key in data:
            action = QAction('&{}'.format(key), self)
            action.triggered.connect(data[key][0])
            if data[key][1]:
                action.setShortcut(data[key][1])
            actions.append(action)
        return actions
