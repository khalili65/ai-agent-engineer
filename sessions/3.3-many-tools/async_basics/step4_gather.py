"""Async basics, step 4: asyncio.gather starts all three downloads together."""
import asyncio
import time


async def download(name, seconds):
    print(f"Starting {name}")
    await asyncio.sleep(seconds)  # pause here; other tasks may run meanwhile
    print(f"Finished {name}")
    return name


async def main():
    results = await asyncio.gather(
        download("A", 3),
        download("B", 2),
        download("C", 1),
    )
    print(results)  # same order as we passed them in


start = time.perf_counter()
asyncio.run(main())  # start the event loop and run main
print(f"Total: {time.perf_counter() - start:.1f} seconds")
