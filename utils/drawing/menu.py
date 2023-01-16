from utils.drawing.toolbar import Toolbar2
import pygame as pg


class Menu:
    def __init__(self, screen):
        self.screen = screen

        self.main_toolbars = []
        self.other_toolbars = []
        self.font = pg.font.SysFont('Arial', 16)
        self.current_toolbar = -1

        self.main_toolbars.append(Toolbar2(self.screen, (0, 0), (1000, 25)))
        self.main_toolbars[0].add_button('file', lambda: self.select_toolbar(1), (10, 0), (42, 20))
        self.main_toolbars[0].add_button('drawing', lambda: self.select_toolbar(2), (57, 0), (76, 20))
        self.main_toolbars[0].add_button('view', lambda: self.select_toolbar(3), (138, 0), (33, 20))
        self.main_toolbars[0].add_button('layers', lambda: self.select_toolbar(4), (176, 0), (40, 20))
        self.main_toolbars[0].add_button('tools', lambda: self.select_toolbar(5), (221, 0), (99, 20))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60)))
        self.main_toolbars[2].add_button('point', lambda: self.screen.plot.create_point(), (10, 0))
        self.main_toolbars[2].add_button('segment', lambda: self.screen.plot.create_segment(), (45, 0))
        self.main_toolbars[2].add_button('more_options', lambda: self.open_toolbar(0), (75, 0), size=(12, 30))
        self.main_toolbars[2].add_button('line', lambda: self.screen.plot.create_line(), (90, 0))
        self.main_toolbars[2].add_button('more_options', lambda: self.open_toolbar(1), (120, 0), size=(12, 30))
        self.main_toolbars[2].add_button('plane', lambda: self.screen.plot.create_plane(), (135, 0))
        self.main_toolbars[2].add_button('more_options', lambda: self.open_toolbar(2), (165, 0), size=(12, 30))
        self.main_toolbars[2].add_button('circle', lambda: print('circle'), (180, 0))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))
        self.main_toolbars[3].add_button('minus', lambda: self.screen.plot.zoom_out(), (10, 0))
        self.main_toolbars[3].add_button('plus', lambda: self.screen.plot.zoom_in(), (45, 0))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))
        self.main_toolbars[4].add_button('empty', lambda: self.open_toolbar(3), (10, 0), size=(200, 30),
                                         text=self.font.render(self.screen.plot.layers[
                                                                   self.screen.plot.current_layer].name,
                                                               False, (0, 0, 0)), text_pos=(5, 7))
        self.main_toolbars[4].add_button('plus', lambda: self.screen.plot.add_layer(
            'Слой ' + str(len(self.screen.plot.layers) + 1)), (215, 0))
        self.main_toolbars[4].add_button('hide', lambda: self.screen.plot.show_hide_layer(True), (250, 0))

        self.main_toolbars.append(Toolbar2(self.screen, (0, 25), (1000, 60), hidden=True))
        self.main_toolbars[5].add_button('distance', lambda: self.screen.plot.get_distance(), (10, 0))
        self.main_toolbars[5].add_button('angle', lambda: self.screen.plot.get_angle(), (45, 0))

        self.other_toolbars.append(Toolbar2(self.screen, (40, 60), (250, 130)))
        self.other_toolbars[-1].add_button('perpendicular',
                                           lambda: self.screen.plot.create_perpendicular(False), (5, 0), (200, 30),
                                           self.font.render('Перпендикуляр', False, (0, 0, 0)), (30, 7), hide_tb=True)
        self.other_toolbars[-1].add_button('parallel',
                                           lambda: self.screen.plot.create_parallel(False), (5, 27), (200, 30),
                                           self.font.render('Параллельно', False, (0, 0, 0)), (30, 7), hide_tb=True)

        self.other_toolbars.append(Toolbar2(self.screen, (85, 60), (295, 201)))
        self.other_toolbars[-1].add_button('perpendicular',
                                           lambda: self.screen.plot.create_perpendicular(True), (5, 0), (200, 30),
                                           self.font.render('Перпендикуляр', False, (0, 0, 0)), (30, 7), hide_tb=True)
        self.other_toolbars[-1].add_button('parallel',
                                           lambda: self.screen.plot.create_parallel(True), (5, 27), (200, 30),
                                           self.font.render('Параллельно', False, (0, 0, 0)), (30, 7), hide_tb=True)
        self.other_toolbars[-1].add_button('horizontal',
                                           lambda: self.screen.plot.create_h_f(f=False), (5, 54), (200, 30),
                                           self.font.render('Горизонталь', False, (0, 0, 0)), (30, 7), hide_tb=True)
        self.other_toolbars[-1].add_button('frontal',
                                           lambda: self.screen.plot.create_h_f(f=True), (5, 81), (200, 30),
                                           self.font.render('Фронталь', False, (0, 0, 0)), (30, 7), hide_tb=True)

        self.other_toolbars.append(Toolbar2(self.screen, (130, 60), (340, 130)))
        self.other_toolbars[-1].add_button('3points',
                                           lambda: self.screen.plot.create_plot_from_3_points(), (5, 0), (200, 30),
                                           self.font.render('3 точки', False, (0, 0, 0)), (30, 7), hide_tb=True)
        self.other_toolbars[-1].add_button('parallel',
                                           lambda: self.screen.plot.create_parallel_plane(), (5, 27), (200, 30),
                                           self.font.render('Параллельно', False, (0, 0, 0)), (30, 7), hide_tb=True)

        self.other_toolbars.append(Toolbar2(self.screen, (5, 60), (250, 70)))
        self.update_layer_list()

    def full_update_toolbars(self):
        pg.draw.rect(self.screen.screen, (255, 255, 255),
                     (0, self.screen.brp[1] - 40, self.screen.brp[0], self.screen.brp[1]))
        if self.current_toolbar != -1:
            self.other_toolbars[self.current_toolbar].draw()
        for toolbar in self.main_toolbars:
            toolbar.draw()

    def select_toolbar(self, index):
        for i in range(1, len(self.main_toolbars)):
            self.main_toolbars[i].hidden = True
        self.main_toolbars[index].hidden = False
        self.screen.plot.full_update()
        self.full_update_toolbars()

    def clicked_on(self, pos):
        if not self.other_toolbars[self.current_toolbar].clicked_on_toolbar(pos):
            self.other_toolbars[self.current_toolbar].hidden = True
            self.current_toolbar = -1
            self.screen.plot.full_update()
            self.full_update_toolbars()
        elif self.other_toolbars[self.current_toolbar].clicked_on(pos):
            self.screen.plot.full_update()
            self.full_update_toolbars()
            return
        for toolbar in self.main_toolbars:
            if toolbar.clicked_on(pos):
                return True

    def open_toolbar(self, index):
        self.other_toolbars[index].hidden = False
        self.other_toolbars[index].draw()
        self.current_toolbar = index

    def update_layer_list(self):
        # TODO: сделать это по-нормальному
        self.other_toolbars[3].buttons.clear()
        self.other_toolbars[3].brp = self.other_toolbars[3].brp[0], 73 + 27 * len(self.screen.plot.layers)
        self.main_toolbars[4].buttons[0].text = self.font.render(
            self.screen.plot.layers[self.screen.plot.current_layer].name, False, (0, 0, 0))
        if self.screen.plot.layers[self.screen.plot.current_layer].hidden:
            self.main_toolbars[4].buttons[2].image = pg.image.load('images\\button_show.bmp')
            self.main_toolbars[4].buttons[2].image_pressed = pg.image.load('images\\button_show_pressed.bmp')
            self.main_toolbars[4].buttons[2].function = lambda: self.screen.plot.show_hide_layer(False)
        else:
            self.main_toolbars[4].buttons[2].image = pg.image.load('images\\button_hide.bmp')
            self.main_toolbars[4].buttons[2].image_pressed = pg.image.load('images\\button_hide_pressed.bmp')
            self.main_toolbars[4].buttons[2].function = lambda: self.screen.plot.show_hide_layer(True)
        self.full_update_toolbars()
        self.screen.plot.full_update()
        i = 0
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(0), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 0), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 0), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(1), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 1), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 1), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(2), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 2), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 2), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(3), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 3), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 3), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(4), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 4), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 4), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(5), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 5), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 5), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(6), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 6), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 6), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(7), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 7), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 7), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(8), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 8), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 8), (202, 27 * i))
        i += 1
        if i == len(self.screen.plot.layers):
            return
        self.other_toolbars[3].add_button(
            'empty', lambda: self.screen.plot.change_current_layer(9), (5, 27 * i), size=(200, 30),
            text=self.font.render(self.screen.plot.layers[i].name, False, (0, 0, 0)), text_pos=(5, 7), hide_tb=True)
        if self.screen.plot.layers[i].hidden:
            self.other_toolbars[3].add_button(
                'show', lambda: self.screen.plot.show_hide_layer(False, 9), (202, 27 * i))
        else:
            self.other_toolbars[3].add_button(
                'hide', lambda: self.screen.plot.show_hide_layer(True, 9), (202, 27 * i))
