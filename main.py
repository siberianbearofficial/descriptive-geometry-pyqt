import pygame as pg
from utils.drawing.real_point import RealPoint as RP
from utils.drawing.real_segment import RealSegment as RS
import utils.maths.angem as ag


def draw_segment(screen, segment, color):
    pg.draw.line(screen, color, segment.p1.tuple(), segment.p2.tuple())


def draw_ag_line(screen, tl_corner, br_corner, axis, line, color):
    # xy projection
    p1_xy = RP.from_point(ag.Point(line.x(0), 0, None), axis, 'xy')
    p2_xy = RP.from_point(ag.Point(line.x(br_corner[1]), 500, None), axis, 'xy')

    segment_xy = RS(p1_xy, p2_xy)
    draw_segment(screen, segment_xy, color)

    # xz projection
    p1_xz = RP.from_point(ag.Point(line.y(z=0), None, 0), axis, 'xz')
    p2_xz = RP.from_point(ag.Point(line.y(z=500), None, 500), axis, 'xz')

    segment_xz = RS(p1_xz, p2_xz)
    draw_segment(screen, segment_xz, color)


def draw_background(screen, tl_corner, br_corner, bg_color):
    rect = pg.Rect(tl_corner, br_corner)
    pg.draw.rect(screen, bg_color, rect)


def draw_ag_segment(screen, segment, axis, color):
    # xy projection
    segment_xy = RS.from_segment(segment, axis, 'xy')
    draw_segment(screen, segment_xy, color)

    # xz projection
    segment_xz = RS.from_segment(segment, axis, 'xz')
    draw_segment(screen, segment_xz, color)


def draw_plot(screen, tl_corner, br_corner):
    axis_l = RP(tl_corner[0], br_corner[1] / 2)
    axis_r = RP(br_corner[0], br_corner[1] / 2)
    axis = RS(axis_l, axis_r)
    draw_segment(screen, axis, (0, 0, 0))

    AB = ag.Segment(ag.Point(120, 50, 50), ag.Point(100, 100, -100))
    # draw_ag_segment(screen, AB, axis, (255, 0, 0))

    # BC = ag.Segment(ag.Point(100, 100, 100), ag.Point(150, 150, 150))
    # draw_ag_segment(screen, BC, axis, (0, 255, 0))

    BC = ag.Segment(ag.Point(100, 100, 100), ag.Point(550, 150, 150))

    draw_ag_line(screen, tl_corner, br_corner, axis, ag.Line(AB.p1, AB.p2), (50, 28, 255))
    draw_ag_line(screen, tl_corner, br_corner, axis, ag.Line(BC.p1, BC.p2), (147, 25, 192))


def main():
    pg.init()
    screen = pg.display.set_mode((640, 480))

    draw_background(screen, (0, 0), (640, 480), (255, 255, 255))
    draw_plot(screen, (0, 0), (640, 480))

    pg.display.flip()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return


if __name__ == '__main__':
    main()
