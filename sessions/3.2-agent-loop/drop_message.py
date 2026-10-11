"""Session 3.2, a common mistake: the reply has no text, so we do not add it to the messages.

This file ends with an error from the API on purpose.
"""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, FUNCTIONS, SYSTEM, SARA

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": SARA}]

reply = client.chat.completions.create(
    model=MODEL, messages=messages, tools=TOOLS).choices[0].message

# THE MISTAKE: the reply has no text, so we skip it. The right line is:
# messages.append(reply)

for call in reply.tool_calls:
    args = json.loads(call.function.arguments)
    result = FUNCTIONS[call.function.name](**args)
    print(f"Tool call: {call.function.name}({args})")
    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

print("Sending the tool results back to the model...")
reply = client.chat.completions.create(
    model=MODEL, messages=messages, tools=TOOLS).choices[0].message
print("Agent:", reply.content)
