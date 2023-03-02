from PyQt5.QtWidgets import QMenuBar, QAction


class MenuBar(QMenuBar):
    def __init__(self, *names):
        super().__init__()

        for name in names:
            self.addAction(QAction('&{}'.format(name), self))

    def connect(self, *funcs):
        actions = self.actions()
        if len(funcs) != len(actions):
            return

        for i in range(len(funcs)):
            actions[i].triggered.connect(funcs[i])

        return self
