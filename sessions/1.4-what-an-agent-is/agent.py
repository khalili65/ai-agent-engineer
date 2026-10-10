"""Session 1.4, way 3: an agent. The model decides the next step in a loop; our code runs the tools."""
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from nova_office import find_booking, prepare_refund
from refund_rule import refund_amount

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

# The tools: plain Python functions the model may ask for
TOOLS = {"find_booking": find_booking, "refund_amount": refund_amount, "prepare_refund": prepare_refund}

def tool(name, description, **inputs):
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": inputs, "required": list(inputs)}}}

TOOL_DESCRIPTIONS = [
    tool("find_booking", "Look up a Nova Travel booking by its booking ID.",
         booking_id={"type": "string"}),
    tool("refund_amount", "Apply the Nova Travel refund rule. Returns the refund in dollars.",
         price={"type": "number"}, days_before_trip={"type": "integer"},
         reason={"type": "string", "enum": ["airline cancelled", "changed mind"]}),
    tool("prepare_refund", "Prepare a refund for a person to approve. It never sends money.",
         booking_id={"type": "string"}, amount={"type": "number"}),
]

messages = [
    {"role": "system", "content": "You are the Nova Travel support agent. Check facts with your "
     "tools. You never send refunds yourself; a person approves every refund. "
     "Answer in two or three short sentences."},
    {"role": "user", "content": sys.argv[1] if len(sys.argv) > 1 else SARA},
]
step = 0
while True:  # the agent loop: the model decides, our code acts
    step += 1
    reply = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOL_DESCRIPTIONS).choices[0].message
    messages.append(reply)
    if not reply.tool_calls:  # no tool call: this is the final answer
        print(f"Step {step}, the model answers:", reply.content)
        break
    for call in reply.tool_calls:
        args = json.loads(call.function.arguments)
        result = TOOLS[call.function.name](**args)
        print(f"Step {step}, the model asks for {call.function.name}({args}) -> {result}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
