import asyncio
import curses
import os
import random
import time
from itertools import cycle
from random import choice, randint

from animation.curses_tools import draw_frame, get_frame_size, read_controls
from animation.fire import fire
from animation.space_garbage import fly_garbage
from animation.stars import blink
from physics import update_speed

TIC_TIMEOUT = 0.1
COROUTINES = []


async def fill_orbit_with_garbage(canvas, width):
    while True:
        path_to_directory = os.path.join('animation', 'garbage')
        filename = random.choice(os.listdir(path_to_directory))

        with open(os.path.join(path_to_directory, filename), "r") as garbage_file:
            frame = garbage_file.read()

        COROUTINES.append(fly_garbage(canvas, random.randint(1, width), frame))

        await asyncio.sleep(0)


def get_rockets():
    rocket_dir = os.path.join('animation', 'rocket')
    rockets = []
    with open(os.path.join(rocket_dir, 'rocket_frame_1.txt'), 'r') as rocket:
        rockets.append(rocket.read())
    with open(os.path.join(rocket_dir, 'rocket_frame_2.txt'), 'r') as rocket:
        rockets.append(rocket.read())

    return rockets


def twice_cycle(iterable):
    for item in cycle(iterable):
        for _ in range(2):
            yield item


async def animate_starship(canvas, row, column):
    rockets = get_rockets()

    frame_height, frame_width = get_frame_size(rockets[0])
    canvas_height, canvas_width = canvas.getmaxyx()

    border_width = 1
    motion_space_height = canvas_height - frame_height - border_width
    motion_space_width = canvas_width - frame_width - border_width

    row_speed, column_speed = 0, 0
    for frame in twice_cycle(rockets):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        row = max(1, min(row + row_speed, motion_space_height))
        column = max(1, min(column + column_speed, motion_space_width))

        if space_pressed:
            COROUTINES.append(fire(canvas, row, column + 2))

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = curses.window.getmaxyx(canvas)
    center_row = round(height / 2)
    center_column = round(width / 2)

    for _ in range(random.randint(500, 2000)):
        distance_from_frame = 2
        symbols = ['+', '*', '.', ':']
        COROUTINES.append(
            blink(canvas,
                  randint(distance_from_frame, height - distance_from_frame),
                  randint(distance_from_frame, width - distance_from_frame),
                  choice(symbols)))
    COROUTINES.append(fill_orbit_with_garbage(canvas, width))
    COROUTINES.append(animate_starship(canvas, center_row, center_column))

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
