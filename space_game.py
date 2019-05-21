import time
import curses
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.stars import generate_stars
from animations.spaceship import animate_spaceship
from animations.space_garbage import fly_garbage
from custom_tools import load_frames_from_dir

TIC_TIMEOUT = 0.1


def draw(canvas):

    # initialisation
    canvas.border()
    canvas.nodelay(True)  # make non block input
    curs_set(False)
    coroutines = []

    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y // 2, max_x // 2

    # load game frames
    spaceship_frames = load_frames_from_dir("./models/spaceship/")
    main_spaceship_frame, *other_spaceship_frames = spaceship_frames
    garbage_frames = load_frames_from_dir("./models/garbage")

    # add one garbage animation
    coroutines.append(fly_garbage(canvas, 10, garbage_frames[0]))

    # add stars animation
    coroutines.extend([star for star in generate_stars(canvas, 100)])

    # add fire animation
    coroutines.append(fire(canvas, center_row, center_column))

    # add spaceship animation
    coroutines.append(animate_spaceship(
        canvas, center_row, center_column, main_spaceship_frame, *other_spaceship_frames
    ))

    # custom event loop
    while coroutines:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
