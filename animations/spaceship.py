from curses_tools import draw_frame, read_controls, get_frame_size
from custom_sleep import async_sleep


async def animate_spaceship(
        canvas, start_row: int,
        start_column: int,
        main_frame: str,
        *other_frames: str
):
    frame_rows, frame_columns = get_frame_size(main_frame)
    border_indent = 1

    # correcting depend on frame size
    corrected_start_column = start_column - (frame_columns // 2)
    current_row, current_column = start_row, corrected_start_column

    max_y, max_x = canvas.getmaxyx()
    min_row, min_column = border_indent, border_indent
    max_row = max_y - frame_rows - border_indent
    max_column = max_x - frame_columns - border_indent

    frames = [main_frame, *other_frames]
    while True:
        diff_rows, diff_columns, press_enter = read_controls(canvas)
        new_row = current_row + diff_rows
        new_column = current_column + diff_columns
        # middle coordinate for correct position when abs(diff_rows) > 1
        current_row = sorted([min_row, max_row, new_row])[1]
        current_column = sorted([min_column, max_column, new_column])[1]

        for frame in frames:
            draw_frame(canvas, current_row, current_column, frame)

            await async_sleep(2)

            # delete previous frame before next one
            draw_frame(canvas, current_row, current_column, frame, negative=True)
