import asyncio
import curses
import os
import random
from itertools import cycle
from random import choice, randint

from curses_tools import draw_frame, get_frame_size, read_controls
from explosion import explode
from obstacles import Obstacle, show_obstacles
from physics import update_speed

TIC_TIMEOUT = 0.1
COROUTINES = []
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISIONS = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(randint(1, 20))

        canvas.addstr(row, column, symbol)
        await sleep(randint(1, 3))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(randint(1, 5))

        canvas.addstr(row, column, symbol)
        await sleep(randint(1, 3))


async def fill_orbit_with_garbage(canvas, width):
    while True:
        path_to_directory = os.path.join('animation', 'garbage')
        filename = random.choice(os.listdir(path_to_directory))
        with open(os.path.join(path_to_directory, filename), "r") as garbage_file:
            frame = garbage_file.read()
        COROUTINES.append(fly_garbage(canvas, random.randint(1, width), frame))
        await sleep(15)


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

        if space_pressed:
            COROUTINES.append(fire(canvas, row, column + 2))

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)

        for obstacle in OBSTACLES.copy():
            if obstacle.has_collision(row, column):
                COROUTINES.append(show_gameover(canvas))
                return


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows, columns = get_frame_size(garbage_frame)
    current_obstacle = Obstacle(row, column, rows, columns)
    OBSTACLES.append(current_obstacle)

    try:
        while row < rows_number:
            if current_obstacle in OBSTACLES_IN_LAST_COLLISIONS:
                OBSTACLES_IN_LAST_COLLISIONS.remove(current_obstacle)
                return

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            current_obstacle.row += speed
    finally:
        OBSTACLES.remove(current_obstacle)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in OBSTACLES.copy():
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                await explode(canvas, row, column)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def show_gameover(canvas):
    with open(os.path.join('animation', 'game_over.txt'), 'r') as gameover:
        gameover = gameover.read()
    height, width = curses.window.getmaxyx(canvas)
    while True:
        draw_frame(canvas, round(height / 3), round(width / 3), gameover)
        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = curses.window.getmaxyx(canvas)
    center_row = round(height / 2)
    center_column = round(width / 2)

    for _ in range(random.randint(50, 200)):
        distance_from_frame = 2
        symbols = ['+', '*', '.', ':']
        COROUTINES.append(
            blink(canvas,
                  randint(distance_from_frame, height - distance_from_frame),
                  randint(distance_from_frame, width - distance_from_frame),
                  choice(symbols)))
    COROUTINES.append(fill_orbit_with_garbage(canvas, width))
    COROUTINES.append(animate_starship(canvas, center_row, center_column))

    loop = asyncio.get_event_loop()
    # loop.create_task(show_obstacles(canvas, OBSTACLES))
    loop.create_task(async_draw(canvas))
    loop.run_forever()


async def async_draw(canvas):
    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        await asyncio.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
