import curses
import time

from animation.fire import fire
from animation.stars import get_stars
from animation.starship import animate_starship
from animation.space_garbage import fly_garbage

TIC_TIMEOUT = 0.1


def draw(canvas):
    with open('animation/garbage/lamp.txt', "r") as garbage_file:
        frame = garbage_file.read()

    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = curses.window.getmaxyx(canvas)
    center_row = round(height / 2)
    center_column = round(width / 2)

    blaze = fire(canvas, center_row, center_column)
    stars = get_stars(canvas, height, width)
    starship = animate_starship(canvas, center_row, center_column)
    garbage = fly_garbage(canvas, column=10, garbage_frame=frame)

    coroutines = [blaze, *stars, starship, garbage]

    while coroutines:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
