"""Session 3.6, step 1: Anna's long message, handled WITHOUT a plan."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from support_tools import ANNA, FUNCTIONS, TOOLS, WAITING_LIST

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_STEPS = 15

messages = [
    {"role": "system", "content": "You are the Nova Travel support agent. Check facts with your "
     "tools. You never send money or change a booking yourself: a person approves every "
     "refund and every change. Read the refund rules before you prepare a refund. "
     "Answer the customer in a short, friendly message."},
    {"role": "user", "content": ANNA},
]

for step in range(1, MAX_STEPS + 1):
    reply = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS).choices[0].message
    messages.append(reply)
    if not reply.tool_calls:  # no tool request: this is the final answer
        print("\nAgent:", reply.content)
        break
    for call in reply.tool_calls:  # the model asks, our code runs the function
        args = json.loads(call.function.arguments)
        result = FUNCTIONS[call.function.name](**args)
        print(f"Step {step}: {call.function.name}({args})")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

print("\nWaiting list for Daniel's team:")
for item in WAITING_LIST:
    print(" ", item)
