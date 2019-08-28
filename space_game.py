import curses
import itertools
import random
import time
from curses import curs_set, wrapper
from typing import Iterable

from obstacles import Obstacle
from curses_tools import draw_frame, get_frame_size, read_controls
from custom_tools import async_sleep, load_frame, load_frames_from_dir
from explosion import explode
from physics import update_speed

TIC_TIMEOUT = 0.1
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

year = 1957
coroutines = []
obstacles = []
obstacles_in_last_collisions = []
spaceship_frame = None


def get_garbage_delay_tics():
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def start_time(one_year_time=15):
    global year
    while True:
        await async_sleep(one_year_time)
        year += 1


async def run_spaceship(canvas, start_row: int, start_column: int, game_over: str):
    global coroutines
    frame_rows, frame_columns = get_frame_size(spaceship_frame)
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

        draw_frame(canvas, current_row, current_column, spaceship_frame)
        previous_frame = spaceship_frame

        if year > 2020 and space_button:
            coroutines.append(
                fire(canvas, current_row, current_column + frame_center_column)
            )

        await async_sleep(1)
        # delete previous frame before next one
        draw_frame(canvas, current_row, current_column, previous_frame, negative=True)

        for obstacle in obstacles:
            if obstacle.has_collision(current_row, current_column):
                await explode(canvas, current_row, current_column)
                coroutines.append(show_gameover(canvas, game_over))
                return


async def show_gameover(canvas, frame: str):
    max_y, max_x = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(frame)
    center_row = (max_y - frame_rows) / 2
    center_column = (max_x - frame_columns) / 2
    while True:
        draw_frame(canvas, center_row, center_column, frame)
        await async_sleep(1)
        draw_frame(canvas, center_row, center_column, frame, negative=True)


async def animate_spaceship(main_frame: str, *other_frames: str):
    global spaceship_frame
    frames = [main_frame, *other_frames]
    for frame in itertools.cycle(frames):
        spaceship_frame = frame
        await async_sleep(2)


async def fill_orbit_with_garbage(canvas, garbage_frames: Iterable[str]):
    while True:
        await async_sleep(1)
        while get_garbage_delay_tics():
            garbage_frame = random.choice(garbage_frames)
            rows_number, columns_number = canvas.getmaxyx()
            start_column = random.randint(0, columns_number - 1)
            coroutines.append(fly_garbage(canvas, start_column, garbage_frame))
            garbage_tics_delay = get_garbage_delay_tics()
            await async_sleep(garbage_tics_delay)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    obstacle = Obstacle(row, column, frame_rows, frame_columns)
    global obstacles
    global obstacles_in_last_collisions
    obstacles.append(obstacle)
    try:
        while row < rows_number:
            obstacle.row = row
            draw_frame(canvas, row, column, garbage_frame)
            await async_sleep(1)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                frame_center_row = row + frame_rows / 2
                frame_center_columns = column + frame_rows / 2
                await explode(canvas, frame_center_row, frame_center_columns)
                return
    finally:
        obstacles.remove(obstacle)


async def fire(canvas, start_row, start_column, rows_speed=-1, columns_speed=0):
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
    global obstacles_in_last_collisions
    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await async_sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
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


def get_start_column(canvas, text: str) -> float:
    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y / 2, max_x / 2
    start_column = center_column - (len(text) / 2)
    return start_column


async def show_year_and_fact(canvas):
    year_row = 2
    phrase_row = 1
    previous_phrase = None
    previous_phrase_column = None
    while True:
        phrase = PHRASES.get(year)
        if phrase:
            if previous_phrase and previous_phrase_column:
                draw_frame(
                    canvas, phrase_row, previous_phrase_column,
                    previous_phrase, negative=True
                )
            phrase_start_column = get_start_column(canvas, phrase)
            draw_frame(canvas, phrase_row, phrase_start_column, phrase)
            previous_phrase = phrase
            previous_phrase_column = phrase_start_column

        message = f'Year: {year}'
        start_year_column = get_start_column(canvas, message)
        draw_frame(canvas, year_row, start_year_column, message)
        await async_sleep(1)
        draw_frame(canvas, year_row, start_year_column, message, negative=True)


def draw(canvas):
    # initialisation
    canvas.border()
    canvas.nodelay(True)  # make non block input
    curs_set(False)

    max_y, max_x = canvas.getmaxyx()
    center_row, center_column = max_y // 2, max_x // 2
    max_row, max_column = max_y - 2, max_x - 2
    footer = canvas.derwin(4, max_x, max_y - 4, 0)

    # load game frames
    spaceship_frames = load_frames_from_dir("./models/spaceship/")
    main_spaceship_frame, *other_spaceship_frames = spaceship_frames
    garbage_frames = load_frames_from_dir("./models/garbage")
    game_over = load_frame("./models/game_over")

    coroutines.append(show_year_and_fact(footer))
    coroutines.append(start_time())
    # add garbage constructor
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_frames))

    # add stars animation
    coroutines.extend([star for star in generate_stars(canvas, 50)])

    # add spaceship animation
    coroutines.append(animate_spaceship(main_spaceship_frame, *other_spaceship_frames))
    coroutines.append(run_spaceship(canvas, max_row - 10, center_column, game_over))

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
