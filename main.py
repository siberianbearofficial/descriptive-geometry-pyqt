import pygame as pg
import pygame_widgets as pw
from pygame_widgets.textbox import TextBox
from utils.drawing.real_point import RealPoint as RP
from utils.drawing.real_segment import RealSegment as RS
import utils.maths.angem as ag


screen = None
axis = None


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


def draw_background(tl_corner, br_corner, bg_color):
    global screen

    rect = pg.Rect(tl_corner, br_corner)
    pg.draw.rect(screen, bg_color, rect)


def draw_ag_segment(screen, segment, axis, color):
    # xy projection
    segment_xy = RS.from_segment(segment, axis, 'xy')
    draw_segment(screen, segment_xy, color)

    # xz projection
    segment_xz = RS.from_segment(segment, axis, 'xz')
    draw_segment(screen, segment_xz, color)


def draw_ag_point(screen, point, axis, color):
    # xy projection
    point_xy = RP.from_point(point, axis, 'xy')
    pg.draw.circle(screen, color, point_xy.tuple(), 2)

    # xz projection
    point_xz = RP.from_point(point, axis, 'xz')
    pg.draw.circle(screen, color, point_xz.tuple(), 2)


def split_by_highest_commas(text):
    layer = 0
    before_comma = ''
    splitted = []
    for letter in text:
        if letter == '(':
            layer += 1
        elif letter == ')':
            layer -= 1
        if letter == ',' and layer == 0:
            splitted.append(before_comma)
            before_comma = ''
        else:
            before_comma += letter
    if before_comma:
        splitted.append(before_comma)
    return splitted


def get_text_before_parathesis(text):
    return text[:text.find('(')]


def get_text_in_higher_parentheses(text):
    return text[text.find('(') + 1:text.rfind(')')]


def execute_command(cmd, args):
    if cmd == 'segment':
        return ag.Segment(args[0], args[1])
    elif cmd == 'point':
        return ag.Point(float(args[0]), float(args[1]), float(args[2]))
    elif cmd == 'line':
        return ag.Line(args[0], args[1])
    elif cmd == 'print':
        print(*args)
        return args
    elif cmd == 'clear':
        draw_background((0, 0), (640, 480), (255, 255, 255))
        draw_plot((0, 0), (640, 480))
        return args
    elif cmd == 'draw':
        draw_ag_content(args)
        return args
    elif cmd == 'help':
        print('Commands:')
        print('segment(point, point) - creates segment')
        print('point(x, y, z) - creates point')
        print('line(point, point) - creates line')
        print('print(*args) - prints args')
        print('clear() - clears screen')
        print('draw(*args) - draws args')
        print('help() - prints this message')
        print()
        print('Some tips:')
        print("Typing command without parentheses won't execute it.")
        print("You can't use variables to store results of commands.")
        print('Typical usage looks like this:')
        print('segment(point(0, 0, 0), point(1, 1, 1))   # this creates segment but doesn\'t draw or print it')
        print('draw(segment(point(0, 0, 0), point(1, 1, 1)))')
        print('print(segment(point(0, 0, 0), point(1, 1, 1)))')
        return args
    else:
        print('Unavailable command: {}. Use "help()" to see all available commands.'.format(cmd))
        return args


def process_command(command):
    command = command.replace(' ', '').lower()

    results = []
    for splitted_by_highest_commas_el in split_by_highest_commas(command):
        cmd, args = get_text_before_parathesis(splitted_by_highest_commas_el), get_text_in_higher_parentheses(splitted_by_highest_commas_el)
        # print('cmd: {}, args: {}'.format(cmd, args))
        if '(' in args:
            # print('Args is command. Processing it recursively.')
            res_of_processing = process_command(args)
            # print('Res of processing:', *res_of_processing)
            res = execute_command(cmd, res_of_processing)
        else:
            if isinstance(args, str):
                args = args.split(',')
            res = execute_command(cmd, args)
            # print('Args is not command. Res:', res)
        results.append(res)
    return results


def output(textbox):
    process_command(textbox.getText())
    textbox.setText('')


def draw_ag_content(args):
    for arg in args:
        if isinstance(arg, ag.Segment):
            draw_ag_segment(screen, arg, axis, (0, 0, 0))
        elif isinstance(arg, ag.Point):
            draw_ag_point(screen, arg, axis, (0, 0, 0))
        elif isinstance(arg, ag.Line):
            draw_ag_line(screen, (0, 0), (640, 480), axis, arg, (0, 0, 0))
        else:
            print('Invalid argument type:', type(arg))


def draw_plot(tl_corner, br_corner):
    global screen
    global axis

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

    tb = TextBox(screen, 10, 10, 500, 30, fontSize=25,
            borderColour=(64, 64, 64), textColour=(20, 20, 20), backgroundColor=(), radius=0, borderThickness=1)
    tb.onSubmit = lambda: output(tb)


def main():
    global screen

    # init
    pg.init()
    screen = pg.display.set_mode((640, 480))
    pg.display.set_caption('Начертательная геометрия')

    # draw some content
    draw_background((0, 0), (640, 480), (255, 255, 255))
    draw_plot((0, 0), (640, 480))

    pg.display.flip()  # update the display

    # main loop
    while True:
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                return

        pw.update(events)
        pg.display.update()


if __name__ == '__main__':
    main()
