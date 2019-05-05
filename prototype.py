import time
import curses
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.stars import generate_stars
from animations.spaceship import animate_spaceship

TIC_TIMEOUT = 0.1


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y // 2, max_x // 2
    canvas.border()
    curs_set(False)

    coroutines = [star for star in generate_stars(canvas, 100)]
    coroutines.append(fire(canvas, center_row, center_column))

    # add spaceship animation
    with open("./models/spaceship_f1") as f1, open("./models/spaceship_f2") as f2:
        spaceship_frames = [f1.read(), f2.read()]
    coroutines.append(animate_spaceship(canvas, center_row, center_column, spaceship_frames))

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
