"""Session 1.3: your first agent. It looks up Sara's booking."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# 1. The tool: a normal Python function (a small stand-in for the company system)
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel",
                "price": "$640.00", "flight": "cancelled by the airline"},
}

def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})

# 2. The tool description: name, what it does, its input
TOOLS = [{"type": "function", "function": {
    "name": "find_booking",
    "description": "Look up a Nova Travel booking by its booking ID.",
    "parameters": {"type": "object",
                   "properties": {"booking_id": {"type": "string"}},
                   "required": ["booking_id"]}}}]

# 3. The agent loop: the model decides, our code acts
messages = [
    {"role": "system", "content": "You are the Nova Travel support agent. Check facts with "
     "your tools. You never send refunds yourself; a person approves every refund. "
     "Answer in two or three short sentences."},
    {"role": "user", "content": "Hi, this is Sara. The airline cancelled my flight to "
     "Lisbon. My booking is NT-4821. Can I get my money back?"},
]
while True:
    reply = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS).choices[0].message
    messages.append(reply)
    if not reply.tool_calls:  # no request for a tool: this is the final answer
        print("Agent:", reply.content)
        break
    for call in reply.tool_calls:  # the model asks, our code runs the function
        args = json.loads(call.function.arguments)
        result = find_booking(**args)
        print(f"Tool call: {call.function.name}({args}) -> {result}")
        messages.append({"role": "tool", "tool_call_id": call.id,
                         "content": json.dumps(result)})
