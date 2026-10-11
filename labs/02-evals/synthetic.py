"""Step 3a: write a few careful synthetic customer messages for the failure we see most.

    uv run python labs/02-evals/synthetic.py

We do not ask for "random test messages". We pick the dimensions ourselves (who writes, what they want,
how they write), and the model only writes the words. Then a person reads every message before it
goes into cases.jsonl.
"""
import itertools
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

CUSTOMERS = ["Leo, booking NT-7240, Madrid, the airline cancelled his flight",
             "Emma, booking NT-5582, Barcelona, trip in 45 days"]
INTENTS = ["asks if the refund she or he asked for last week is approved yet",
           "asks how much money would come back, without deciding to cancel",
           "asks if the money can arrive before Friday"]
TONES = ["polite", "short and angry"]

PROMPT = """Write one message that a customer sends to the support of Nova Travel, a small travel agency.
Customer: {customer}. What they want: {intent}. Tone: {tone}.
Write only the message, one to three sentences, with the booking ID in it."""

if __name__ == "__main__":
    for customer, intent, tone in itertools.product(CUSTOMERS, INTENTS, TONES):
        response = client.chat.completions.create(
            model=os.getenv("MODEL", "gpt-4o-mini"), temperature=1,
            messages=[{"role": "user", "content": PROMPT.format(customer=customer, intent=intent, tone=tone)}])
        message = response.choices[0].message.content.strip().strip('"')
        print(json.dumps({"customer": customer.split(",")[0], "intent": intent[:30], "tone": tone,
                          "message": message}))
