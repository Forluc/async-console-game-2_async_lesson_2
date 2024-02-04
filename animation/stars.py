import asyncio
import curses
from random import choice, randint


async def blink(canvas, row, column, symbol='*', offset_tics=None):
    if offset_tics is None:
        offset_tics = [20, 3, 5, 3]
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(offset_tics[0]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(offset_tics[1]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(offset_tics[2]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(offset_tics[3]):
            await asyncio.sleep(0)


def get_stars(canvas, row, column):
    symbols = ['+', '*', '.', ':']
    number_of_stars = randint(50, 200)

    return [blink(canvas,
                  randint(0, row - 1),
                  randint(0, column - 1),
                  choice(symbols),
                  [randint(0, num) for num in [20, 3, 5, 3]])
            for _ in range(number_of_stars)]
