"""Session 2.2: a streamed reply. The words arrive piece by piece while the model writes."""
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

INSTRUCTIONS = ("You are the Nova Travel support agent. Booking NT-4821: Sara, Lisbon, "
                "5 nights, flight + hotel, $640.00, flight cancelled by the airline. "
                "Rule: if the airline cancels, the customer gets a full refund. "
                "A person on our team approves every refund, so say that. "
                "Explain the refund and the next steps in about 150 words.")
QUESTION = "Hi, this is Sara. The airline cancelled my flight to Lisbon. Can I get my money back?"

start = time.time()
first = None
pieces = 0
stream = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": QUESTION},
    ],
    stream=True,
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        if first is None:
            first = time.time() - start
        pieces += 1
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
print(f"First words after {first:.1f} s. Full reply after {time.time() - start:.1f} s. Pieces: {pieces}")
