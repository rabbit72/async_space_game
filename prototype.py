import time
import curses
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.stars import generate_stars

TIC_TIMEOUT = 0.1


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
