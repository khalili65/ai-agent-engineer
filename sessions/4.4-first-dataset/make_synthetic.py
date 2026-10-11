"""Make synthetic test cases: the model writes the customer's message, our rules write the expected result.

    uv run python sessions/4.4-first-dataset/make_synthetic.py 24

Every candidate is one mix of three dimensions: tone x request x edge.
The candidates go to synthetic_candidates.jsonl. A person reads every one before it joins the dataset.
"""
import json
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from support_agent_v1 import BOOKINGS, change_fee, refund_amount

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
HERE = Path(__file__).parent

# The three dimensions.
TONES = ["polite", "angry", "very short, no greeting", "chatty, with a small story"]
REQUESTS = {
    "changed_mind": "cancel the trip because they changed their mind, and get their money back",
    "airline_cancelled": "the airline cancelled their flight, so they want their money back",
    "change_dates": "move the whole trip a few days later",
    "refund_status": "ask if the refund they asked for last week is approved yet",
    "baggage": "ask how many bags they can take",
}
EDGES = ["none", "14_days", "15_days", "typo_in_id"]


def pick_booking(request, edge, rng):
    """Choose a booking that fits the request and the edge, or None if the mix makes no sense."""
    if edge == "14_days":
        ids = [b for b in BOOKINGS if BOOKINGS[b]["days_before_trip"] == 14]
    elif edge == "15_days":
        ids = [b for b in BOOKINGS if BOOKINGS[b]["days_before_trip"] == 15]
    else:
        ids = list(BOOKINGS)
    if request == "airline_cancelled":
        ids = [b for b in ids if BOOKINGS[b]["flight"] == "cancelled by the airline"]
    else:
        ids = [b for b in ids if BOOKINGS[b]["flight"] != "cancelled by the airline"]
    if request == "baggage" and edge != "none":
        return None  # the bag rules do not depend on the days or the booking number
    return rng.choice(ids) if ids else None


def typo(booking_id, rng):
    """A booking number with a small typo: two digits swapped, or one digit missing."""
    digits = booking_id[3:]
    if rng.random() < 0.5 and digits[2] != digits[3]:
        return "NT-" + digits[:2] + digits[3] + digits[2]
    return "NT-" + digits[:3]


def expected_for(request, edge, booking):
    """The expected result comes from Daniel's rules, written as code. The model never writes it."""
    if edge == "typo_in_id":
        return {"tool": "find_booking", "refund": False}  # ask again, never guess the number
    if request in ("changed_mind", "airline_cancelled"):
        amount = refund_amount(booking, request)
        if amount == 0:
            return {"refund": False, "no_promise": True}
        return {"tool": "prepare_refund", "amount": amount, "no_promise": True}
    if request == "change_dates":
        return {"tool": "prepare_change", "fee": change_fee(booking), "no_promise": True}
    if request == "refund_status":
        return {"refund": False, "no_promise": True}
    return {"tool": "get_policy", "refund": False}


PROMPT = """Write one message that a customer sends to the support team of Nova Travel,
a small online travel agency.
Customer name: {name}
Booking number, write it exactly like this: {id_text}
Trip: {trip}
What the customer wants: {want}
Tone: {tone}
Write only the message, one to three sentences. Do not write any amounts of money, fees or rules."""


def write_message(name, id_text, trip, want, tone):
    response = client.chat.completions.create(
        model=MODEL, temperature=1.0,
        messages=[{"role": "user", "content": PROMPT.format(
            name=name, id_text=id_text, trip=trip, want=want, tone=tone)}])
    tokens = response.usage.prompt_tokens, response.usage.completion_tokens
    return response.choices[0].message.content.strip(), tokens


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    rng = random.Random(44)
    mixes = [(t, r, e) for t in TONES for r in REQUESTS for e in EDGES]
    rng.shuffle(mixes)

    candidates, used_in, used_out = [], 0, 0
    for tone, request, edge in mixes:
        if len(candidates) == count:
            break
        booking_id = pick_booking(request, edge, rng)
        if booking_id is None:
            continue  # this mix makes no sense, skip it
        booking = BOOKINGS[booking_id]
        id_text = typo(booking_id, rng) if edge == "typo_in_id" else booking_id
        message, (tin, tout) = write_message(booking["customer"], id_text, booking["trip"],
                                             REQUESTS[request], tone)
        used_in, used_out = used_in + tin, used_out + tout
        tags = [request] + ([] if edge == "none" else [edge])
        candidates.append({"candidate": f"s{len(candidates) + 1:02}", "message": message,
                           "expected": expected_for(request, edge, booking), "tags": tags,
                           "mix": {"tone": tone, "request": request, "edge": edge,
                                   "booking": booking_id, "id_text": id_text}})
        print(f"s{len(candidates):02}  {tone:<26} {request:<18} {edge:<11} {message}")

    with open(HERE / "synthetic_candidates.jsonl", "w") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")
    cost = used_in * 0.15 / 1e6 + used_out * 0.60 / 1e6
    print(f"\n{len(candidates)} candidates · {used_in:,} input + {used_out:,} output tokens · ${cost:.4f}")
