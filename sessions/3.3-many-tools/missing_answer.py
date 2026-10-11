"""Session 3.3, step 4: what happens if we answer only one of the tool calls."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, SYSTEM, MARIA, run_tool

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": MARIA}]
reply = client.chat.completions.create(
    model=MODEL, messages=messages, tools=TOOLS).choices[0].message
messages.append(reply)
print("Tool calls:", [call.id for call in reply.tool_calls])

first = reply.tool_calls[0]  # we answer ONLY the first call (a mistake on purpose)
result = run_tool(first.function.name, json.loads(first.function.arguments))
messages.append({"role": "tool", "tool_call_id": first.id, "content": json.dumps(result)})
print("Answered only:", first.id)

client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
