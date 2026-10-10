"""Session 2.2: Sara's question, sent with the Chat Completions API."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY (and OPENAI_BASE_URL, MODEL) from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

INSTRUCTIONS = ("You are the Nova Travel support agent. Booking NT-4821: Sara, Lisbon, "
                "5 nights, flight + hotel, $640.00, flight cancelled by the airline. "
                "Rule: if the airline cancels, the customer gets a full refund. "
                "A person on our team approves every refund, so say that. "
                "Answer in two short sentences.")
QUESTION = "Hi, this is Sara. The airline cancelled my flight to Lisbon. Can I get my money back?"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": QUESTION},
    ],
)
print(response.choices[0].message.content)
print("Tokens:", response.usage.prompt_tokens, "in,", response.usage.completion_tokens, "out")
