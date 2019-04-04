import time
import asyncio
import curses
from curses import wrapper
from curses import curs_set


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        canvas.refresh()
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        canvas.refresh()
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)
        canvas.refresh()
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curs_set(False)

    star_1 = blink(canvas, 5, 20)
    star_2 = blink(canvas, 7, 25)
    star_3 = blink(canvas, 5, 16)
    while True:
        star_1.send(None)
        star_2.send(None)
        star_3.send(None)


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
    # time.sleep(2000)
