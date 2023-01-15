from utils.drawing.toolbar import Toolbar2
import pygame as pg


class Menu:
    def __init__(self, screen):
        self.screen = screen

        self.main_toolbars = []
        self.other_toolbars = []
        self.font = pg.font.SysFont('arial', 12)
        self.current_toolbar = -1

        self.main_toolbars.append(Toolbar2(self.screen, (0, 0), (1000, 25)))
        self.main_toolbars[0].add_button('file', lambda: self.select_toolbar(1), (10, 0), (42, 20))
        self.main_toolbars[0].add_button('drawing', lambda: self.select_toolbar(2), (57, 0), (76, 20))
        self.main_toolbars[0].add_button('view', lambda: self.select_toolbar(3), (138, 0), (33, 20))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60)))
        self.main_toolbars[2].add_button('point', lambda: self.screen.plot.create_point(), (10, 0))
        self.main_toolbars[2].add_button('segment', lambda: self.screen.plot.create_segment(), (45, 0))
        self.main_toolbars[2].add_button('more_options', lambda: self.open_toolbar(0), (75, 0), size=(12, 30))
        self.main_toolbars[2].add_button('line', lambda: self.screen.plot.create_line(), (90, 0))
        self.main_toolbars[2].add_button('more_options', lambda: self.open_toolbar(1), (120, 0), size=(12, 30))
        self.main_toolbars[2].add_button('plane', lambda: self.screen.plot.create_plane(), (135, 0))
        self.main_toolbars[2].add_button('more_options', lambda: print('more options'), (165, 0), size=(12, 30))
        self.main_toolbars[2].add_button('circle', lambda: print('circle'), (180, 0))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))
        self.main_toolbars[3].add_button('minus', lambda: self.screen.plot.zoom_out(), (10, 0))
        self.main_toolbars[3].add_button('plus', lambda: self.screen.plot.zoom_in(), (45, 0))

        self.other_toolbars.append(Toolbar2(self.screen, (40, 60), (250, 130)))
        self.other_toolbars[-1].add_button('perpendicular', lambda: self.screen.plot.create_segment(), (5, 0), (200, 30),
                                           self.font.render('Перпендикуляр', False, (0, 0, 0)), (30, 9))
        self.other_toolbars[-1].add_button('parallel', lambda: print('Параллельно'), (5, 27), (200, 30),
                                           self.font.render('Параллельно', False, (0, 0, 0)), (30, 9))

        self.other_toolbars.append(Toolbar2(self.screen, (85, 60), (295, 130)))
        self.other_toolbars[-1].add_button('perpendicular', lambda: print('Перпендикуляр'), (5, 0), (200, 30),
                                           self.font.render('Перпендикуляр', False, (0, 0, 0)), (30, 9))
        self.other_toolbars[-1].add_button('parallel', lambda: print('Параллельно'), (5, 27), (200, 30),
                                           self.font.render('Параллельно', False, (0, 0, 0)), (30, 9))

    def full_update_toolbars(self):
        pg.draw.rect(self.screen.screen, (255, 255, 255),
                     (0, self.screen.brp[1] - 40, self.screen.brp[0], self.screen.brp[1]))
        for toolbar in self.main_toolbars:
            toolbar.draw()

    def select_toolbar(self, index):
        for i in range(1, 4):
            self.main_toolbars[i].hidden = True
        self.main_toolbars[index].hidden = False
        self.full_update_toolbars()
        self.screen.plot.full_update()

    def clicked_on(self, pos):
        if not self.other_toolbars[self.current_toolbar].clicked_on_toolbar(pos):
            self.other_toolbars[self.current_toolbar].hidden = True
            self.full_update_toolbars()
            self.screen.plot.full_update()
        elif self.other_toolbars[self.current_toolbar].clicked_on(pos):
            self.full_update_toolbars()
            self.screen.plot.full_update()
            return
        for toolbar in self.main_toolbars:
            if toolbar.clicked_on(pos):
                return True

    def open_toolbar(self, index):
        self.other_toolbars[index].hidden = False
        self.other_toolbars[index].draw()
        self.current_toolbar = index
