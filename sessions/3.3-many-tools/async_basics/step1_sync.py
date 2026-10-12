"""Async basics, step 1: normal Python. Three downloads, one after the other."""
import time


def download(name, seconds):
    print(f"Starting {name}")
    time.sleep(seconds)  # pretend download: the whole program stops and waits
    print(f"Finished {name}")
    return name


start = time.perf_counter()
download("A", 3)
download("B", 2)
download("C", 1)
print(f"Total: {time.perf_counter() - start:.1f} seconds")
