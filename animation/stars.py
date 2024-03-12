import asyncio
import curses


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
