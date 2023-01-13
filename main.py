import pygame as pg
import pygame_widgets as pw

from utils.drawing.screen import Screen


def main():
    # init
    pg.init()

    screen = Screen(640, 480, 'Начертательная геометрия')

    pg.display.flip()  # update the display

    # main loop
    while True:
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                return
            elif event.type == pg.MOUSEBUTTONDOWN:
                screen.clicked()

        pw.update(events)
        pg.display.update()


if __name__ == '__main__':
    main()
