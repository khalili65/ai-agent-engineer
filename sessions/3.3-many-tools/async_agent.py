"""Session 3.3, step 7: the support agent runs independent tool calls at the same time."""
import asyncio
import json
import os
import time
from dotenv import load_dotenv
from openai import AsyncOpenAI
from nova_tools import TOOLS, SYSTEM, MARIA, WAITING_LIST
from async_tools import run_tool_async

load_dotenv()
client = AsyncOpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_STEPS = 10

async def run_agent(user_message):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}]
    for step in range(1, MAX_STEPS + 1):
        response = await client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS)
        reply = response.choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        calls = reply.tool_calls
        start = time.perf_counter()
        results = await asyncio.gather(*(   # all calls of this reply at the same time
            run_tool_async(c.function.name, json.loads(c.function.arguments)) for c in calls))
        print(f"Model call {step}: {len(calls)} tool call(s), "
              f"tools took {time.perf_counter() - start:.1f} seconds")
        for call, result in zip(calls, results):  # one answer per call id, same order
            print(f"  {call.function.name} -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return "Stopped: too many steps. A person takes over."

start = time.perf_counter()
answer = asyncio.run(run_agent(MARIA))
print("Agent:", answer)
print("Waiting list:", WAITING_LIST)
print(f"Total time: {time.perf_counter() - start:.1f} seconds")
