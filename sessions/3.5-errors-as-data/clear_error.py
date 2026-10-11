"""Session 3.5, step 3: an error message that tells the model what to do."""
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from nova_system import CUSTOMERS, SYSTEM_PROMPT, TOOL_FUNCTIONS, TOOLS, WAITING_LIST

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

def run_agent(messages):
    for step in range(1, 7):  # at most six steps
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            args = json.loads(call.function.arguments)
            try:
                result = TOOL_FUNCTIONS[call.function.name](**args)
            except Exception as error:
                result = f"Error: {error}"  # the message tells the model what to do
            print(f"Step {step}: {call.function.name}({args}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "(stopped after six steps without an answer)"

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
for name in sys.argv[1:] or ["emma"]:  # one or more customer messages, in order
    print("Customer:", CUSTOMERS[name])
    messages.append({"role": "user", "content": CUSTOMERS[name]})
    print("Agent:", run_agent(messages))
print("Waiting list:", WAITING_LIST)
