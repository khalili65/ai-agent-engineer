"""Session 3.6, step 2: the same message, WITH a visible plan (an update_plan tool)."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from support_tools import ANNA, FUNCTIONS, TOOLS, WAITING_LIST

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_STEPS = 20

# 1. The plan tool: the model writes the whole list, our code keeps it and prints it
PLAN = []
MARK = {"pending": "[ ]", "in_progress": "[>]", "done": "[x]"}

def update_plan(items):
    PLAN[:] = items
    done = sum(item["status"] == "done" for item in PLAN)
    print(f"\n  PLAN  {done} of {len(PLAN)} done")
    for item in PLAN:
        print(f"  {MARK[item['status']]} {item['task']}")
    open_items = [item["task"] for item in PLAN if item["status"] != "done"]
    if not open_items:
        return f"Plan saved. All {len(PLAN)} items are done. Now answer the customer."
    return (f"Plan saved. {done} of {len(PLAN)} done. Next: {open_items[0]}. "
            "Mark it in_progress, do it, then mark it done.")

PLAN_TOOL = {"type": "function", "function": {
    "name": "update_plan",
    "description": "Write your plan, or update it. Always send the full list of items. "
                   "Each item has a short task and a status: pending, in_progress or done.",
    "strict": True,
    "parameters": {"type": "object", "properties": {
        "items": {"type": "array", "items": {"type": "object", "properties": {
            "task": {"type": "string"},
            "status": {"type": "string", "enum": ["pending", "in_progress", "done"]}},
            "required": ["task", "status"], "additionalProperties": False}}},
        "required": ["items"], "additionalProperties": False}}}

FUNCTIONS = {**FUNCTIONS, "update_plan": update_plan}

# 2. New sentences in the system prompt: facts first, then the plan
messages = [
    {"role": "system", "content": "You are the Nova Travel support agent. Check facts with your "
     "tools. You never send money or change a booking yourself: a person approves every "
     "refund and every change. Read the refund rules before you prepare a refund. "
     "Answer the customer in a short, friendly message. "
     "First, look up every booking and read the refund rules. Then write a plan with "
     "update_plan: one item for each thing the customer asks, written as the action you "
     "will take, like 'Prepare refund of 640 dollars for NT-4821'. "
     "Work on one item at a time: mark it in_progress, do it, and mark it done. "
     "Give your final answer only when every item is done."},
    {"role": "user", "content": ANNA},
]

# 3. The same loop, plus one check: the agent may not stop while the plan has open items
for step in range(1, MAX_STEPS + 1):
    reply = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS + [PLAN_TOOL],
        parallel_tool_calls=False).choices[0].message
    messages.append(reply)
    if not reply.tool_calls:
        open_items = [item["task"] for item in PLAN if item["status"] != "done"]
        if open_items:  # our code checks the plan before the agent may stop
            print(f"\n  CHECK  {len(open_items)} open item(s), the agent goes on")
            messages.append({"role": "user", "content": f"Your plan has open items: {open_items}. "
                             "Finish them, then answer."})
            continue
        print("\nAgent:", reply.content)
        break
    for call in reply.tool_calls:
        args = json.loads(call.function.arguments)
        result = FUNCTIONS[call.function.name](**args)
        if call.function.name != "update_plan":
            print(f"      step {step}: {call.function.name}({args})")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

print("\nWaiting list for Daniel's team:")
for item in WAITING_LIST:
    print(" ", item)
