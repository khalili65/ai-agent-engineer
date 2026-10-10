"""Lab 1: the Nova Travel support agent, with no framework."""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import PENDING_REFUNDS, TOOL_DESCRIPTIONS, TOOLS

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

INSTRUCTIONS = (
    "You are the Nova Travel support agent. Always check facts with your tools before you answer. "
    "Read the refund rules before you decide about a refund. You never send money: use prepare_refund, "
    "and tell the customer that a person will approve it. Answer in two or three short sentences."
)


def run(message: str, max_steps: int = 8) -> str:
    messages = [{"role": "system", "content": INSTRUCTIONS}, {"role": "user", "content": message}]
    for _ in range(max_steps):
        reply = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_DESCRIPTIONS).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = TOOLS[call.function.name](**args)
            print(f"  tool: {call.function.name}({args})")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "Sorry, I could not finish. A person from our team will help you."


if __name__ == "__main__":
    question = "Hi, this is Sara. The airline cancelled my flight to Lisbon. My booking is NT-4821. Can I get my money back?"
    print("Customer:", question)
    print("Agent:", run(question))
    print("Waiting for approval:", PENDING_REFUNDS)
