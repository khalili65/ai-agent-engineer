"""Does the order of two replies change the judge's choice?

    uv run python sessions/4.6-trust-your-judge/position_bias.py

A pairwise judge reads two replies to the same customer message and picks the better one.
We ask it twice for every pair: once with the replies in the order X, Y and once in the order Y, X.
A fair judge picks the same reply both times. If it picks "A" both times (or "B" both times),
the place in the list decided, not the reply. That is called position bias.
"""
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o-mini"

PAIRWISE = """You compare two replies of the Nova Travel support agent to the same customer message.
Which reply is better for the customer? A better reply is correct, clear, and makes no promise
that only a person can give.
First write one short sentence with your reason.
Then write one letter on the last line: A or B."""


def pick(message, first, second):
    """Asks the judge once. Returns "A" or "B" and the tokens used."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[{"role": "system", "content": PAIRWISE},
                  {"role": "user", "content": f"Customer: {message}\n\nReply A: {first}\n\nReply B: {second}"}])
    last_line = response.choices[0].message.content.strip().splitlines()[-1]
    return ("A" if "A" in last_line.upper() else "B"), response.usage


rows = [json.loads(line) for line in (Path(__file__).parent / "data" / "labels.jsonl").read_text().splitlines()]
pairs = [(rows[i], rows[i + 1]) for i in range(0, len(rows), 2)]  # two replies to the same message

same_reply = always_a = always_b = 0
tokens = 0
for x, y in pairs:
    first, u1 = pick(x["message"], x["reply"], y["reply"])   # order X, Y
    second, u2 = pick(x["message"], y["reply"], x["reply"])  # order Y, X
    tokens += u1.total_tokens + u2.total_tokens
    if first != second:      # A then B, or B then A: the same reply won both times
        same_reply += 1
        result = "same reply both times"
    elif first == "A":
        always_a += 1
        result = "picked A both times: the order decided"
    else:
        always_b += 1
        result = "picked B both times: the order decided"
    print(f"{x['id']} vs {y['id']}   order 1: {first}   order 2: {second}   {result}")

print(f"\n{len(pairs)} pairs, each judged in both orders")
print(f"Same reply both times:  {same_reply}")
print(f"First place both times: {always_a}")
print(f"Second place both times: {always_b}")
print(f"Tokens {tokens}")
