"""Session 1.4: ask the model to apply the refund rule, and compare it with the function."""
import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
from refund_rule import refund_amount

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

RULES = ("Nova Travel refund rules: If the airline cancels, full refund. If the customer changes "
         "their mind more than 14 days before the trip, refund the price minus a 50 dollar fee. "
         "Otherwise, no refund.")
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 14
CASE = {"price": 380.00, "reason": "changed mind", "days_before_trip": DAYS}  # John

start = time.perf_counter()
print("Function:", refund_amount(**CASE), f"({(time.perf_counter() - start) * 1000:.3f} ms)")

for run in range(1, 11):
    start = time.perf_counter()
    reply = client.chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": RULES + " Answer with the refund in dollars, only the number."},
        {"role": "user", "content": str(CASE)},
    ])
    seconds = time.perf_counter() - start
    print(f"Model run {run}:", reply.choices[0].message.content,
          f"({seconds:.2f} s, {reply.usage.total_tokens} tokens)")
