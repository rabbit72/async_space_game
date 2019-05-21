import os
import asyncio
from typing import Tuple


async def async_sleep(times: int):
    for _ in range(times):
        await asyncio.sleep(0)


def load_frame(path_to_framefile: str) -> str:
    with open(path_to_framefile, "r", encoding="utf-8") as file:
        _frame = file.read()
    return _frame


def load_frames_from_dir(_path: str) -> Tuple[str]:
    _frames = []
    for file_name in os.listdir(_path):
        abs_file_path = os.path.abspath(os.path.join(_path, file_name))
        if not os.path.isfile(abs_file_path):
            continue
        _frames.append(load_frame(abs_file_path))
    return tuple(_frames)
