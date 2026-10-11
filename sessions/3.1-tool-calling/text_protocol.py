"""Session 3.1, step 1: tool calling with NO tools feature, only plain text.

The system prompt tells the model to write one line, CALL find_booking <booking_id>,
when it needs a booking. Our code reads that line, runs the function, and sends
the result back as text. The model only writes; our code does the work.
"""
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY (and MODEL) from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# The tool: a normal Python function (a small stand-in for the booking system)
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel",
                "price": "$640.00", "flight": "cancelled by the airline"},
}

def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})

# Our text protocol, written in plain English
SYSTEM = """You are the Nova Travel support agent. You cannot see bookings yourself.
When you need a booking, reply with exactly one line and nothing else:
CALL find_booking <booking_id>
Our system then sends you a message that starts with RESULT.
After that, answer the customer in two or three short sentences.
You never send refunds yourself; a person approves every refund."""

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")


def run(customer_message):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": customer_message}]
    for step in range(1, 4):  # at most three model calls
        text = client.chat.completions.create(
            model=MODEL, messages=messages).choices[0].message.content
        print(f"Step {step}, the model wrote: {text!r}")
        messages.append({"role": "assistant", "content": text})

        if not text.startswith("CALL "):  # no CALL line: this is the final answer
            return text

        # Our parser: three words, CALL, the tool name, the booking ID
        _, name, booking_id = text.split()
        result = find_booking(booking_id)
        print(f"Our code ran {name}({booking_id!r}) -> {result}")
        messages.append({"role": "user", "content": "RESULT " + json.dumps(result)})


if __name__ == "__main__":
    # Sara's message by default, or the customer message you type after the file name
    run(" ".join(sys.argv[1:]) or SARA)
