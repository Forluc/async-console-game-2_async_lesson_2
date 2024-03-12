import asyncio
import os
from itertools import cycle

from animation.curses_tools import draw_frame, get_frame_size, read_controls
from physics import update_speed


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

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
