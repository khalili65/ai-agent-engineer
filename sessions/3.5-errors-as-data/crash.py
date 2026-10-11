"""Session 3.5, step 1: a tool fails, and the whole agent crashes."""
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from nova_system import BOOKINGS, CUSTOMERS, SYSTEM_PROMPT, TOOLS, get_refund_rules, prepare_refund

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

def find_booking(booking_id):
    return BOOKINGS[booking_id]  # first version: no check at all

TOOL_FUNCTIONS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules,
                  "prepare_refund": prepare_refund}

def run_agent(messages):
    for step in range(1, 7):  # at most six steps
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"Step {step}: {call.function.name}({args})")
            result = TOOL_FUNCTIONS[call.function.name](**args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "(stopped after six steps without an answer)"

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
for name in sys.argv[1:] or ["emma"]:  # one or more customer messages, in order
    print("Customer:", CUSTOMERS[name])
    messages.append({"role": "user", "content": CUSTOMERS[name]})
    print("Agent:", run_agent(messages))
