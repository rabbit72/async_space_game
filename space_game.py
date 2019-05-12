import time
import curses
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.stars import generate_stars
from animations.spaceship import animate_spaceship

TIC_TIMEOUT = 0.1


def draw(canvas):

    # initialisation
    canvas.border()
    canvas.nodelay(True)  # make non block input
    curs_set(False)

    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y // 2, max_x // 2

    coroutines = [star for star in generate_stars(canvas, 100)]
    coroutines.append(fire(canvas, center_row, center_column))

    # add spaceship animation
    with open("./models/spaceship_f1") as f1, open("./models/spaceship_f2") as f2:
        frame_1 = f1.read()
        frame_2 = f2.read()
    coroutines.append(animate_spaceship(
        canvas, center_row, center_column, frame_1, frame_2
    ))

    # custom event loop
    while coroutines:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
