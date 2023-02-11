import utils.history.serializable as serializable
from pygame_widgets.textbox import TextBox
import pygame as pg


class AttributesWindow:
    def __init__(self, screen, obj, pos=(10, 70)):
        self.screen = screen
        self.obj = obj
        self.size = (300, 300)
        self.pos = pos
        self.dict = self.obj.ag_object.__dict__

        self.font1 = pg.font.SysFont('Courier', 12)
        self.font2 = pg.font.SysFont('Courier', 16)

        self.name_textbox = TextBox(self.screen.screen, self.pos[0] + 75, self.pos[1] + 30, 200, 25,
                               inactiveColour=(255, 255, 255), activeColour=(200, 200, 200), textColour=(0, 0, 0),
                               borderColour=(64, 64, 64), radius=3, borderThickness=1,
                               font=self.font2)
        self.name_textbox.text = list(obj.name)
        self.name_textbox.cursorPosition = len(obj.name)
        self.name_textbox.onTextChanged = lambda: self.change_obj_name(''.join(self.name_textbox.text))

        self.pos_to_write = 0
        self.text_boxes = []

    def change_obj_name(self, name):
        self.obj.name = name

    def draw(self):
        pg.draw.rect(self.screen.screen, (195, 195, 195), (self.pos, self.size), border_radius=5)
        pg.draw.rect(self.screen.screen, (80, 80, 80), (self.pos, self.size), 2, 5)
        self.screen.screen.blit(self.font2.render(self.obj.ag_object.__class__.__name__, False, (0, 0, 0)),
                                (self.pos[0] + 10, self.pos[1] + 10))
        self.screen.screen.blit(self.font1.render('Имя:', False, (0, 0, 0)),
                                (self.pos[0] + 10, self.pos[1] + 35))
        self.screen.screen.blit(self.font1.render('Цвет:', False, (0, 0, 0)),
                                (self.pos[0] + 10, self.pos[1] + 60))
        pg.draw.rect(self.screen.screen, self.obj.color, (self.pos[0] + 75, self.pos[1] + 58, 40, 16))
        self.pos_to_write = 80
        for attribute in serializable.angem_objects[serializable.angem_class_by_name[self.obj.ag_object.__class__.__name__]]:
            self.draw_attributes((attribute,))
        self.name_textbox.show()

    def draw_attributes(self, obj):
        level = len(obj) - 1
        dct = self.dict
        for i in range(len(obj) - 1):
            dct = dct[obj[i]]
            if not isinstance(dct, list) and not isinstance(dct, tuple):
                dct = dct.__dict__
        class_name = dct[obj[-1]].__class__
        dct = dct[obj[-1]]
        if isinstance(dct, int) or isinstance(dct, float):
            index = len(self.text_boxes)
            self.screen.screen.blit(self.font1.render(f'{obj[-1]}:', False, (0, 0, 0)),
                                    (self.pos[0] + 10 + 20 * level, self.pos[1] + self.pos_to_write))
            self.text_boxes.append(TextBox(self.screen.screen, self.pos[0] + 75 + 20 * level, self.pos[1] + self.pos_to_write, 150, 18,
                                           inactiveColour=(255, 255, 255), activeColour=(200, 200, 200),
                                           textColour=(0, 0, 0),
                                           borderColour=(64, 64, 64), radius=3, borderThickness=1,
                                           font=self.font1))
            self.text_boxes[-1].text = list(str(dct))
            self.text_boxes[-1].cursorPosition = len(str(obj))
            self.text_boxes[-1].onTextChanged = lambda: self.set_attribute(obj, ''.join(self.text_boxes[index].text))
            self.pos_to_write += 20
        elif isinstance(dct, list) or isinstance(dct, tuple):
            for i in range(len(dct)):
                self.screen.screen.blit(self.font1.render(f'{obj[-1]}[{i}]:', False, (0, 0, 0)),
                                        (self.pos[0] + 10 + 20 * level, self.pos[1] + self.pos_to_write))
                self.pos_to_write += 20
                self.draw_attributes(obj + (i,))
        else:
            self.screen.screen.blit(self.font1.render(f'{obj[-1]}:', False, (0, 0, 0)),
                                    (self.pos[0] + 10 + 20 * level, self.pos[1] + self.pos_to_write))
            self.pos_to_write += 20
            for attribute in serializable.angem_objects[class_name]:
                self.draw_attributes(obj + (attribute,))

    def set_attribute(self, obj, value):
        dct = self.dict
        if value == '':
            value = 0
        else:
            try:
                value = float(value)
            except Exception:
                return
        for i in range(len(obj) - 1):
            dct = dct[obj[i]].__dict__
        dct[obj[-1]] = value

    def point_on_window(self, pos):
        if self.pos[0] < pos[0] < self.pos[0] + self.size[0] and self.pos[1] < pos[1] < self.pos[1] + self.size[1]:
            return True
        return False

    def clicked(self, pos):
        pass

    def destroy(self):
        self.name_textbox.hide()
        for textbox in self.text_boxes:
            textbox.hide()
