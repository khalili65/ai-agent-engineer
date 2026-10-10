"""Session 2.3, step 3: structured output. Every message becomes a clean ticket record."""
import os
from dotenv import load_dotenv
from openai import OpenAI
from ticket import Ticket  # the shape of one ticket (ticket.py)

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

MESSAGES = [
    "Hi, this is Sara. The airline cancelled my flight to Lisbon. "
    "My booking is NT-4821. Can I get my money back?",
    "Hello, Tom here, booking NT-5307. Can I move my Rome hotel two days later? "
    "We fly out tomorrow morning.",
    "Hi! Do your Barcelona trips include the airport transfer? We are thinking about July.",
    "Hi, this is Lukas, booking NT-6190. I changed my mind about Paris in December. "
    "Can I cancel and get my money back?",
]

for text in MESSAGES:
    reply = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Turn the customer message into a Nova Travel ticket."},
            {"role": "user", "content": text},
        ],
        response_format=Ticket,  # the API makes the model follow this shape
    ).choices[0].message
    ticket = reply.parsed  # a real Ticket object, not text
    print(ticket)
