import asyncio
import curses
import os
import random
from itertools import cycle
from random import choice, randint

from curses_tools import draw_frame, get_frame_size, read_controls
from explosion import explode
from obstacles import Obstacle
from physics import update_speed

TIC_TIMEOUT = 0.1
coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1956
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def get_text_for_info_frame(info_frame):
    global year
    while True:
        await sleep(2)
        year += 1
        message = f'Year {year} - {PHRASES.get(year, "")}'
        info_frame.addstr(1, 1, message)
        await asyncio.sleep(0)


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


async def fill_orbit_with_garbage(canvas, column_max):
    while True:
        delay = get_garbage_delay_tics(year)
        if delay:
            path_to_directory = os.path.join('animation', 'garbage')
            filename = random.choice(os.listdir(path_to_directory))
            with open(os.path.join(path_to_directory, filename), "r") as garbage_file:
                frame = garbage_file.read()
            coroutines.append(fly_garbage(canvas, random.randint(1, column_max), frame))
            await sleep(delay)
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

        draw_frame(canvas, row, column, frame)

        if space_pressed and year >= 2020:
            displacement_of_firegun = 2
            coroutines.append(fire(canvas, row, column + displacement_of_firegun))

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)

        for obstacle in obstacles.copy():
            if obstacle.has_collision(row, column):
                coroutines.append(show_gameover(canvas))
                return


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows, columns = get_frame_size(garbage_frame)
    current_obstacle = Obstacle(row, column, rows, columns)
    obstacles.append(current_obstacle)

    try:
        while row < rows_number:
            if current_obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(current_obstacle)
                return

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            current_obstacle.row += speed
    finally:
        obstacles.remove(current_obstacle)


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
        for obstacle in obstacles.copy():
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
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
    canvas_rows, canvas_columns = curses.window.getmaxyx(canvas)
    frame_rows, frame_columns = get_frame_size(gameover)
    row = (canvas_rows - frame_rows) // 2
    column = (canvas_columns - frame_columns) // 2
    while True:
        draw_frame(canvas, row, column, gameover)
        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    row_max, column_max = canvas.getmaxyx()
    center_row = round(row_max / 2)
    center_column = round(column_max / 2)

    for _ in range(random.randint(50, 200)):
        distance_from_frame = 2
        symbols = ['+', '*', '.', ':']
        coroutines.append(
            blink(canvas,
                  randint(distance_from_frame, row_max - distance_from_frame),
                  randint(distance_from_frame, column_max - distance_from_frame),
                  choice(symbols)))
    coroutines.append(fill_orbit_with_garbage(canvas, column_max))
    coroutines.append(animate_starship(canvas, center_row, center_column))

    info_frame_length = 60
    info_frame_height = 4
    info_frame = canvas.derwin(row_max - info_frame_height, column_max - info_frame_length)
    coroutines.append(get_text_for_info_frame(info_frame))

    loop = asyncio.get_event_loop()
    loop.create_task(async_draw(canvas, info_frame))
    loop.run_forever()


async def async_draw(canvas, info_frame):
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        info_frame.border()
        info_frame.refresh()
        await asyncio.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
