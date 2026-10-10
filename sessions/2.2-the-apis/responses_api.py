"""Session 2.2: the same question, sent with the OpenAI Responses API (needs an OpenAI key)."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

INSTRUCTIONS = ("You are the Nova Travel support agent. Booking NT-4821: Sara, Lisbon, "
                "5 nights, flight + hotel, $640.00, flight cancelled by the airline. "
                "Rule: if the airline cancels, the customer gets a full refund. "
                "A person on our team approves every refund, so say that. "
                "Answer in two short sentences.")
QUESTION = "Hi, this is Sara. The airline cancelled my flight to Lisbon. Can I get my money back?"

response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=QUESTION,
)
print(response.output_text)
print("Output items:", [item.type for item in response.output])
print("Tokens:", response.usage.input_tokens, "in,", response.usage.output_tokens, "out")
