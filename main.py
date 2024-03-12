import asyncio
import curses
import os
import random
import time
from random import choice, randint

from animation.fire import fire
from animation.space_garbage import fly_garbage
from animation.stars import blink
from animation.starship import animate_starship

TIC_TIMEOUT = 0.1

COROUTINES = []


def get_stars(canvas, height, width):
    symbols = ['+', '*', '.', ':']
    number_of_stars = random.randint(50, 200)
    for _ in range(number_of_stars):
        COROUTINES.append(blink(canvas, randint(1, height - 1), randint(1, width - 1), choice(symbols)))


async def fill_orbit_with_garbage(canvas, width):
    while True:
        path_to_directory = os.path.join('animation', 'garbage')
        filename = random.choice(os.listdir(path_to_directory))

        with open(os.path.join(path_to_directory, filename), "r") as garbage_file:
            frame = garbage_file.read()

        COROUTINES.append(fly_garbage(canvas, random.randint(1, width), frame))

        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = curses.window.getmaxyx(canvas)
    center_row = round(height / 2)
    center_column = round(width / 2)

    COROUTINES.append(fire(canvas, center_row, center_column))
    COROUTINES.append(animate_starship(canvas, center_row, center_column))
    COROUTINES.append(fill_orbit_with_garbage(canvas, width))
    get_stars(canvas, height, width)

    while COROUTINES:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
