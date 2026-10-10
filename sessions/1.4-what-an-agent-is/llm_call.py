"""Session 1.4, way 1: one LLM call. No tools, no steps."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

reply = client.chat.completions.create(model=MODEL, messages=[
    {"role": "system", "content": "You are the Nova Travel support agent. You never send refunds "
     "yourself; a person approves every refund. Answer in two or three short sentences."},
    {"role": "user", "content": SARA},
]).choices[0].message
print("Model:", reply.content)
