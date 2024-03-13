import asyncio
import curses
from random import randint


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
