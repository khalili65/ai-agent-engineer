"""Async basics, step 3: async functions, but we await them one by one."""
import asyncio
import time


async def download(name, seconds):
    print(f"Starting {name}")
    await asyncio.sleep(seconds)  # pause here; other tasks may run meanwhile
    print(f"Finished {name}")
    return name


async def main():
    await download("A", 3)  # wait until A is done
    await download("B", 2)  # only then start B
    await download("C", 1)  # only then start C


start = time.perf_counter()
asyncio.run(main())  # start the event loop and run main
print(f"Total: {time.perf_counter() - start:.1f} seconds")
