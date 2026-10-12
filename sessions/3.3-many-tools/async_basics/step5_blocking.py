"""Async basics, step 5: a normal sleep inside async def blocks the event loop."""
import asyncio
import time


async def download(name, seconds):
    print(f"Starting {name}")
    time.sleep(seconds)  # wrong inside async code: nothing else can run
    print(f"Finished {name}")
    return name


async def main():
    results = await asyncio.gather(
        download("A", 3),
        download("B", 2),
        download("C", 1),
    )
    print(results)


start = time.perf_counter()
asyncio.run(main())
print(f"Total: {time.perf_counter() - start:.1f} seconds")
