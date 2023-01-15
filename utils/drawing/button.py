import pygame as pg


class Button:
    def __init__(self, image, function, pos, size=(30, 30), text=None, text_pos=(0, 0)):
        self.image = pg.image.load('images\\button_' + image + '.bmp')
        self.image_pressed = pg.image.load('images\\button_' + image + '_pressed.bmp')
        self.p1 = pos
        self.p2 = pos[0] + size[0], pos[1] + size[1]
        self.function = function
        self.pressed = False
        self.text = text
        self.text_pos = text_pos

    def draw(self, screen):
        if self.pressed:
            screen.screen.blit(self.image_pressed, self.p1)
        else:
            screen.screen.blit(self.image, self.p1)
        if self.text is not None:
            screen.screen.blit(self.text, (self.p1[0] + self.text_pos[0], self.p1[1] + self.text_pos[1]))

    def click(self, screen, click_pos):
        if self.p1[0] < click_pos[0] < self.p2[0] and self.p1[1] < click_pos[1] < self.p2[1]:
            self.pressed = True
            self.draw(screen)
            screen.update()
            self.function()
            self.pressed = False
            self.draw(screen)
            screen.update()
            return True
        return False
