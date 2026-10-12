"""Async basics, step 2: calling an async function does not run it."""
import asyncio


async def download(name, seconds):
    print(f"Starting {name}")
    await asyncio.sleep(seconds)  # pause here; other tasks may run meanwhile
    print(f"Finished {name}")
    return name


result = download("A", 3)  # no await, no event loop
print(result)
