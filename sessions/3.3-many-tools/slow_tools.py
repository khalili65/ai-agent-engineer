"""Session 3.3, step 6: the same tool calls, one by one and at the same time."""
import asyncio
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, SYSTEM, MARIA
from async_tools import run_tool_async

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

reply = client.chat.completions.create(
    model=MODEL, tools=TOOLS,
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": MARIA}],
).choices[0].message
calls = [(c.function.name, json.loads(c.function.arguments)) for c in reply.tool_calls]
print("Tool calls:", calls)

async def one_by_one():
    return [await run_tool_async(name, args) for name, args in calls]

async def at_the_same_time():
    return await asyncio.gather(*(run_tool_async(name, args) for name, args in calls))

start = time.perf_counter()
asyncio.run(one_by_one())
print(f"One by one:       {time.perf_counter() - start:.1f} seconds")

start = time.perf_counter()
results = asyncio.run(at_the_same_time())
print(f"At the same time: {time.perf_counter() - start:.1f} seconds")
for result in results:
    print("  ", result)
