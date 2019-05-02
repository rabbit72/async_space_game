import time
import random
import asyncio
import curses
from curses import wrapper
from curses import curs_set

TIC_TIMEOUT = 0.1


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        start_offset = random.randint(0, 30)
        for _ in range(start_offset):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
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


def generate_stars(canvas, quantity: int, symbols: iter = "+*.:") -> list:
    used_coordinates = set()
    min_row, min_column = 1, 1
    max_y, max_x = canvas.getmaxyx()
    max_row, max_column = max_y - 2, max_x - 2

    for _ in range(quantity):

        row = random.randint(min_row, max_row)
        column = random.randint(min_row, max_column)
        while (row, column) in used_coordinates:
            row = random.randint(min_row, max_row)
            column = random.randint(min_row, max_column)
        used_coordinates.add((row, column))

        symbol = random.choice(symbols)
        yield blink(canvas, row, column, symbol)


def draw(canvas):
    canvas.border()
    curs_set(False)
    coroutines = [star for star in generate_stars(canvas, 100)]
    center_row, center_column = curses.LINES // 2, curses.COLS // 2
    coroutines.append(fire(canvas, center_row, center_column))
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

        if not coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
