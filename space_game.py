import time
import curses
import random
from curses import wrapper
from curses import curs_set
from animations.fire import fire
from animations.stars import generate_stars
from animations.spaceship import animate_spaceship
from animations.space_garbage import fly_garbage
from custom_tools import load_frames_from_dir
from custom_tools import async_sleep
from typing import Iterable


TIC_TIMEOUT = 0.1
COROUTINES = []


def draw(canvas):
    # initialisation
    canvas.border()
    canvas.nodelay(True)  # make non block input
    curs_set(False)

    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y // 2, max_x // 2
    min_row, min_column = 1, 1
    max_row, max_column = max_y - 2, max_x - 2

    # load game frames
    spaceship_frames = load_frames_from_dir("./models/spaceship/")
    main_spaceship_frame, *other_spaceship_frames = spaceship_frames
    garbage_frames = load_frames_from_dir("./models/garbage")

    # add garbage constructor
    COROUTINES.append(fill_orbit_with_garbage(canvas, garbage_frames))

    # add stars animation
    COROUTINES.extend([star for star in generate_stars(canvas, 100)])

    # add fire animation
    COROUTINES.append(fire(canvas, center_row, center_column))

    # add spaceship animation
    COROUTINES.append(animate_spaceship(
        canvas, max_row, center_column, main_spaceship_frame, *other_spaceship_frames
    ))

    # custom event loop
    while COROUTINES:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


async def fill_orbit_with_garbage(canvas, garbage_frames: Iterable[str]):
    while True:
        garbage_frame = random.choice(garbage_frames)
        rows_number, columns_number = canvas.getmaxyx()
        start_column = random.randint(0, columns_number - 1)

        COROUTINES.append(fly_garbage(canvas, start_column, garbage_frame))

        await async_sleep(random.randint(8, 13))


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
