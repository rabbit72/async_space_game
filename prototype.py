import time
import random
import curses
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.blink import blink

TIC_TIMEOUT = 0.1


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
    center_row, center_column = curses.LINES // 2, curses.COLS // 2
    canvas.border()
    curs_set(False)

    coroutines = [star for star in generate_stars(canvas, 100)]
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
