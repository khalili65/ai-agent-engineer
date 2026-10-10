"""Session 2.3, step 5: check the ticket with our own rule, and retry with the error."""
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError, field_validator
from ticket import Ticket

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

class CheckedTicket(Ticket):  # the same shape, plus one rule of Nova Travel
    @field_validator("booking_id")
    @classmethod
    def real_booking_id(cls, value):
        if value is not None and not re.fullmatch(r"NT-\d{4}", value):
            raise ValueError("must be NT- and four digits, like NT-4821. "
                             "If the customer's ID is not complete, use null. Never invent digits.")
        return value

NADIA = ("Hi, Nadia here. My booking is NT-739, I think. The hotel in Prague says it is "
         "closed for repairs, and I arrive tomorrow! Please help.")

messages = [
    {"role": "system", "content": "Turn the customer message into a Nova Travel ticket. "
     "Copy the booking ID exactly as the customer wrote it."},
    {"role": "user", "content": NADIA},
]
for attempt in range(1, 4):  # at most three tries
    reply = client.chat.completions.parse(
        model=MODEL, messages=messages, response_format=Ticket).choices[0].message
    try:
        ticket = CheckedTicket.model_validate_json(reply.content)
        print(f"Try {attempt}: valid ->", ticket)
        break
    except ValidationError as error:
        print(f"Try {attempt}: not valid ->", error)
        messages.append({"role": "assistant", "content": reply.content})
        messages.append({"role": "user", "content": f"This ticket is not valid:\n{error}\nPlease fix it."})
else:
    print("Still not valid after three tries. A person reads this message.")
