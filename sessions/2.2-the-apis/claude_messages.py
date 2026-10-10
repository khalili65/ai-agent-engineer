"""Session 2.2: the same question, sent with the Claude Messages API (needs an Anthropic key)."""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()  # reads ANTHROPIC_API_KEY from the .env file
client = anthropic.Anthropic()
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")

INSTRUCTIONS = ("You are the Nova Travel support agent. Booking NT-4821: Sara, Lisbon, "
                "5 nights, flight + hotel, $640.00, flight cancelled by the airline. "
                "Rule: if the airline cancels, the customer gets a full refund. "
                "A person on our team approves every refund, so say that. "
                "Answer in two short sentences.")
QUESTION = "Hi, this is Sara. The airline cancelled my flight to Lisbon. Can I get my money back?"

response = client.messages.create(
    model=MODEL,
    max_tokens=4000,
    system=INSTRUCTIONS,
    messages=[{"role": "user", "content": QUESTION}],
)
for block in response.content:  # a list of blocks: pick the text blocks
    if block.type == "text":
        print(block.text)
print("Tokens:", response.usage.input_tokens, "in,", response.usage.output_tokens, "out")
