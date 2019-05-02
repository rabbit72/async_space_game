from curses_tools import draw_frame
from custom_sleep import async_sleep


async def animate_spaceship(canvas, start_row: int, start_column: int, frames: list):
    while True:
        for frame in frames:
            draw_frame(canvas, start_row, start_column, frame)
            canvas.refresh()

            await async_sleep(10)

            # стираем предыдущий кадр, прежде чем рисовать новый
            draw_frame(canvas, start_row, start_column, frame, negative=True)
