"""Session 2.4: the support agent from session 1.3, with the system prompt as an input.

The other files in this folder import `run_agent` and try different system prompts.
"""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY (and MODEL) from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# The tool: a normal Python function (a small stand-in for the company system)
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel",
                "price": "$640.00", "flight": "cancelled by the airline"},
}

def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})

TOOLS = [{"type": "function", "function": {
    "name": "find_booking",
    "description": "Look up a Nova Travel booking by its booking ID.",
    "parameters": {"type": "object",
                   "properties": {"booking_id": {"type": "string"}},
                   "required": ["booking_id"]}}}]

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

def run_agent(system_prompt, user_message=SARA):
    """The agent loop from session 1.3. Returns the final answer."""
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}]
    while True:
        reply = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:  # no request for a tool: this is the final answer
            return reply.content
        for call in reply.tool_calls:  # the model asks, our code runs the function
            args = json.loads(call.function.arguments)
            result = find_booking(**args)
            print(f"  Tool call: {call.function.name}({args})")
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
