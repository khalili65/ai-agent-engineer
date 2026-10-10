"""Session 1.4, way 2: a workflow. Our code decides the steps; the model only writes the reply."""
import os
import re
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
MESSAGE = sys.argv[1] if len(sys.argv) > 1 else SARA

# Step 1: find the booking (the booking number is in the message)
booking_id = re.search(r"NT-\d+", MESSAGE).group()
booking = find_booking(booking_id)
print("Step 1, find the booking:", booking)

# Step 2: check the refund rule (a plain Python function)
reason = "airline cancelled" if booking["flight"] == "cancelled by the airline" else "changed mind"
amount = refund_amount(booking["price"], reason, booking["days_before_trip"])
print("Step 2, check the rule:", reason, "->", amount)

# Step 3: prepare the refund; it waits for a person (Daniel's rule)
refund = prepare_refund(booking_id, amount)
print("Step 3, prepare the refund:", refund)

# Step 4: one model call writes the reply with these facts
reply = client.chat.completions.create(model=MODEL, messages=[
    {"role": "system", "content": "You are the Nova Travel support agent. Write a short, kind reply "
     "to the customer in two or three sentences. Use only the facts you are given."},
    {"role": "user", "content": f"Customer message: {MESSAGE}\nBooking: {booking}\nRefund: {refund}"},
]).choices[0].message
print("Step 4, write the reply:", reply.content)
