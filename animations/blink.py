import random
import asyncio
import curses


async def blink(canvas, row, column, symbol="*"):
    while True:

        start_offset = random.randint(10, 25)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(start_offset):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
