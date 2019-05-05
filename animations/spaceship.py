from curses_tools import draw_frame, read_controls, get_frame_size
from custom_sleep import async_sleep


async def animate_spaceship(
        canvas, start_row: int,
        start_column: int,
        main_frame: str,
        *other_frames: str
):
    frame_rows, frame_columns = get_frame_size(main_frame)
    canvas.nodelay(True)  # make non block input

    # correcting depend on frame size
    corrected_start_column = start_column - (frame_columns // 2)
    current_row, current_column = start_row, corrected_start_column

    frames = [main_frame, *other_frames]
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
