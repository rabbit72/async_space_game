import curses
import itertools
import random
import time
from curses import curs_set, wrapper
from typing import Iterable

import obstacles
from curses_tools import draw_frame, get_frame_size, read_controls
from custom_tools import async_sleep, load_frames_from_dir
from physics import update_speed

TIC_TIMEOUT = 0.1
COROUTINES = []
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISIONS = []
SPACESHIP_FRAME = None


async def run_spaceship(canvas, start_row: int, start_column: int):
    frame_rows, frame_columns = get_frame_size(SPACESHIP_FRAME)
    border_indent = 1
    # correcting depend on frame size
    frame_center_column = (frame_columns // 2)
    corrected_start_column = start_column - frame_center_column
    current_row, current_column = start_row, corrected_start_column

    max_y, max_x = canvas.getmaxyx()
    min_row, min_column = border_indent, border_indent
    max_row = max_y - frame_rows - border_indent
    max_column = max_x - frame_columns - border_indent

    row_speed = column_speed = 0
    new_row = current_row
    new_column = current_column
    while True:
        diff_rows, diff_columns, space_button = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, diff_rows, diff_columns
        )
        new_row += row_speed
        new_column += column_speed
        # middle coordinate for correct position when abs(diff_rows) > 1
        current_row = sorted([min_row, max_row, new_row])[1]
        current_column = sorted([min_column, max_column, new_column])[1]

        draw_frame(canvas, current_row, current_column, SPACESHIP_FRAME)
        previous_frame = SPACESHIP_FRAME

        if space_button:
            global COROUTINES
            COROUTINES.append(
                fire(canvas, current_row, current_column + frame_center_column)
            )

        await async_sleep(1)
        # delete previous frame before next one
        draw_frame(canvas, current_row, current_column, previous_frame, negative=True)


async def animate_spaceship(main_frame: str, *other_frames: str):
    global SPACESHIP_FRAME
    frames = [main_frame, *other_frames]
    for frame in itertools.cycle(frames):
        SPACESHIP_FRAME = frame
        await async_sleep(2)


async def fill_orbit_with_garbage(canvas, garbage_frames: Iterable[str]):
    while True:
        garbage_frame = random.choice(garbage_frames)
        rows_number, columns_number = canvas.getmaxyx()
        start_column = random.randint(0, columns_number - 1)

        COROUTINES.append(fly_garbage(canvas, start_column, garbage_frame))

        await async_sleep(random.randint(8, 13))


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    frame_size = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    obstacle = obstacles.Obstacle(row, column, *frame_size)
    global OBSTACLES
    global OBSTACLES_IN_LAST_COLLISIONS
    OBSTACLES.append(obstacle)
    try:
        while row < rows_number:
            obstacle.row = row
            draw_frame(canvas, row, column, garbage_frame)
            await async_sleep(1)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            if obstacle in OBSTACLES_IN_LAST_COLLISIONS:
                OBSTACLES_IN_LAST_COLLISIONS.remove(obstacle)
                return
    finally:
        OBSTACLES.remove(obstacle)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await async_sleep(1)
    canvas.addstr(round(row), round(column), 'O')
    await async_sleep(1)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()
    global OBSTACLES_IN_LAST_COLLISIONS
    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await async_sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                return


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
        offset = random.randint(5, 25)
        yield blink(canvas, row, column, offset, symbol)


async def blink(canvas, row, column, offset_tics: int, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await async_sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await async_sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await async_sleep(5)

        canvas.addstr(row, column, symbol)
        await async_sleep(3)


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
    COROUTINES.append(obstacles.show_obstacles(canvas, OBSTACLES))

    # add stars animation
    COROUTINES.extend([star for star in generate_stars(canvas, 100)])

    # add spaceship animation
    COROUTINES.append(animate_spaceship(main_spaceship_frame, *other_spaceship_frames))
    COROUTINES.append(run_spaceship(canvas, max_row, center_column))

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


if __name__ == '__main__':
    curses.update_lines_cols()
    wrapper(draw)
