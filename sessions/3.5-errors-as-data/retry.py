"""Session 3.5, step 4: a temporary failure gets a retry; a bad input goes back to the model."""
import json
import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
from nova_system import CUSTOMERS, SYSTEM, SYSTEM_PROMPT, TOOL_FUNCTIONS, TOOLS

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

def call_tool(name, args):
    for attempt in range(1, 4):  # at most three tries
        try:
            return TOOL_FUNCTIONS[name](**args)
        except TimeoutError:  # temporary: wait a little, then try again
            print(f"  try {attempt}: timeout")
            if attempt < 3:
                time.sleep(attempt)  # wait 1 second, then 2 seconds
        except Exception as error:  # a bad input: the model can repair it
            return f"Error: {error}"
    return "Error: The booking system did not answer in time."

def run_agent(messages):
    for step in range(1, 7):  # at most six steps
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            args = json.loads(call.function.arguments)
            result = call_tool(call.function.name, args)
            print(f"Step {step}: {call.function.name}({args}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "(stopped after six steps without an answer)"

SYSTEM["slow_calls"] = int(sys.argv[2]) if len(sys.argv) > 2 else 2  # how slow the system is today
name = sys.argv[1] if len(sys.argv) > 1 else "sara"
print("Customer:", CUSTOMERS[name])
messages = [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": CUSTOMERS[name]}]
print("Agent:", run_agent(messages))
