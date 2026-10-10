"""Session 2.3, step 1: ask for the ticket facts in plain words, then try to read them with code."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY (and OPENAI_BASE_URL, MODEL) from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

reply = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You read customer messages for Nova Travel. Give the "
         "booking ID, the request type (refund, change or question), the reason, "
         "and if it is urgent."},
        {"role": "user", "content": SARA},
    ],
).choices[0].message
print(reply.content)

ticket = json.loads(reply.content)  # our code needs data, not a nice text
print(ticket["booking_id"])
