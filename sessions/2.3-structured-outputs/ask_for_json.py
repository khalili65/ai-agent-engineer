"""Session 2.3, step 2: ask for JSON in the prompt, five times, and count how often code can read it."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

readable = 0
for attempt in range(1, 6):
    text = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You read customer messages for Nova Travel. Give the "
             "booking ID, the request type (refund, change or question), the reason, "
             "and if it is urgent. Answer in JSON."},
            {"role": "user", "content": SARA},
        ],
    ).choices[0].message.content
    try:
        ticket = json.loads(text)
        readable += 1
        print(f"Try {attempt}: OK    keys: {list(ticket)}")
    except json.JSONDecodeError as error:
        print(f"Try {attempt}: FAIL  starts with {text[:7]!r} -> {error}")
print(f"Code could read {readable} of 5 replies.")
