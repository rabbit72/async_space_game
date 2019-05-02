import asyncio


async def async_sleep(times: int):
    for _ in range(times):
        await asyncio.sleep(0)
