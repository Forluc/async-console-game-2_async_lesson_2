import asyncio
import os

from animation.curses_tools import draw_frame, get_frame_size, read_controls
from itertools import cycle


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

    for frame in twice_cycle(rockets):
        row_offset, column_offset, space_pressed = read_controls(canvas)

        row = max(1, min(row + row_offset, motion_space_height))
        column = max(1, min(column + column_offset, motion_space_width))

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
