from curses_tools import draw_frame, read_controls
from custom_sleep import async_sleep


async def animate_spaceship(canvas, start_row: int, start_column: int, frames: list):
    canvas.nodelay(True)  # make non block input
    corrected_start_column = start_column - 2  # correcting depend on frame size
    current_row, current_column = start_row, corrected_start_column

    while True:
        diff_rows, diff_columns, press_enter = read_controls(canvas)
        current_row += diff_rows
        current_column += diff_columns

        for frame in frames:
            draw_frame(canvas, current_row, current_column, frame)
            canvas.refresh()

            await async_sleep(2)

            # delete previous frame before next one
            draw_frame(canvas, current_row, current_column, frame, negative=True)
