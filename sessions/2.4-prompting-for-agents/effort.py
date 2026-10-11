"""Session 2.4: the same harder task with three reasoning effort levels, three runs each."""
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
# A reasoning model: it can think before it answers.
REASONING_MODEL = os.getenv("REASONING_MODEL", "gpt-5.6-luna")

RULES = """You check refund requests for Nova Travel.
Refund rules:
- The airline cancels the flight: full refund.
- The customer changes their mind: refund minus a fee, only if it is more than 14 days before the trip.
  Otherwise, no refund."""

TASK = """Today is 2 March. Here are this morning's refund requests.
1. Sara, NT-4821, Lisbon. The airline cancelled her flight.
2. Tom, NT-3307, Rome, trip starts 1 April. He changed his mind.
3. Lena, NT-5150, Paris, trip starts 16 March. She changed her mind.
4. Ravi, NT-6012, Athens, trip starts 17 March. He changed his mind.
For each request, write one short line: the name and full refund, refund minus a fee, or no refund."""

# The correct answers, worked out by hand (Lena: exactly 14 days, Ravi: 15 days).
CORRECT = {"Sara": "full refund", "Tom": "minus a fee", "Lena": "no refund", "Ravi": "minus a fee"}

def count_right(answer):
    lines = answer.lower().splitlines()
    return sum(any(name.lower() in line and result in line for line in lines)
               for name, result in CORRECT.items())

for effort in ["none", "low", "high"]:
    print(f"=== effort: {effort} ===")
    for run in range(1, 4):
        start = time.time()
        response = client.chat.completions.create(
            model=REASONING_MODEL, reasoning_effort=effort,
            messages=[{"role": "system", "content": RULES},
                      {"role": "user", "content": TASK}])
        seconds = time.time() - start
        answer = response.choices[0].message.content
        thinking = response.usage.completion_tokens_details.reasoning_tokens
        print(f"run {run}: {count_right(answer)} of 4 right, "
              f"reasoning tokens: {thinking}, time: {seconds:.1f} s")
        print("   ", " | ".join(line.strip() for line in answer.splitlines() if line.strip()))
    print()
