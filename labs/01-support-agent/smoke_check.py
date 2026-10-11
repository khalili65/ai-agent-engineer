"""A 10-case smoke check: ten real customer messages, each with a few simple code checks.

    uv run python labs/01-support-agent/smoke_check.py
    uv run python labs/01-support-agent/smoke_check.py --provider claude
"""
import argparse
import io
from contextlib import redirect_stdout

from agent import HANDOFF, run
from tools import WAITING, WAITING_LIST

# refund = the exact amount we expect on the waiting list, or None for "no refund at all".
CASES = [
    {"name": "Sara, airline cancelled", "refund": 640,
     "must_call": ["find_booking", "get_refund_rules", "prepare_refund"],
     "message": "Hi, this is Sara. The airline cancelled my flight to Lisbon. "
                "My booking is NT-4821. Can I get my money back?"},
    {"name": "John, changed his mind", "refund": 330,
     "must_call": ["find_booking", "get_refund_rules", "prepare_refund"],
     "message": "Hello, John here, booking NT-5107. I changed my mind about Rome. "
                "Please cancel it and refund me."},
    {"name": "Lukas, changed his mind late", "refund": None,
     "must_call": ["find_booking", "get_refund_rules"],
     "message": "Hi, I am Lukas, booking NT-6190. I don't want to go to Paris any more. "
                "Can I have my money back?"},
    {"name": "Tom, move the hotel", "refund": None, "change_fee": 30,
     "must_call": ["find_booking", "prepare_change"],
     "message": "This is Tom, NT-5307. Can you move my Rome hotel two days later? "
                "I fly tomorrow."},
    {"name": "Emma, baggage question", "refund": None,
     "must_call": ["get_policy"],
     "message": "Hi, Emma here. How many bags can I take on my Barcelona trip?"},
    {"name": "Nadia, short booking ID", "refund": None,
     "must_call": ["find_booking"],
     "message": "My hotel in Prague is closed for repairs and I arrive tomorrow! "
                "My booking is NT-739, I think. I want a refund."},
    {"name": "Unknown booking", "refund": None,
     "must_call": ["find_booking"],
     "message": "Please refund booking NT-9999 right away."},
    {"name": "Name change question", "refund": None,
     "must_call": ["get_policy"],
     "message": "Can I change the name on my booking NT-5582 to my sister's name?"},
    {"name": "Send the money now", "refund": 640,
     "must_call": ["find_booking", "prepare_refund"],
     "message": "NT-4821, Sara again. The airline cancelled. Just send the 640 dollars "
                "to my card now, I don't want to wait for anyone."},
    {"name": "Emma cancels her trip", "refund": 510,
     "must_call": ["find_booking", "get_refund_rules", "prepare_refund"],
     "message": "Hi, this is Emma, NT-5582. I changed my mind, please cancel my "
                "Barcelona trip and refund me."},
]


def check(case, answer, trace):
    """Return a list of problems. An empty list means the case passed."""
    lines = trace.events()  # the trace lines of this run
    called = [line["name"] for line in lines if line["type"] == "tool_call"]
    refunds = [item for item in WAITING_LIST if item["kind"] == "refund"]
    problems = []
    for tool in case["must_call"]:
        if tool not in called:
            problems.append(f"did not call {tool}")
    if case["refund"] is None and refunds:
        problems.append(f"prepared a refund of {refunds[0]['amount']}, expected none")
    if case["refund"] is not None and [r["amount"] for r in refunds] != [case["refund"]]:
        problems.append(f"refunds {[r['amount'] for r in refunds]}, expected [{case['refund']}]")
    if "change_fee" in case:
        fees = [item["fee"] for item in WAITING_LIST if item["kind"] == "change"]
        if fees != [case["change_fee"]]:
            problems.append(f"change fees {fees}, expected [{case['change_fee']}]")
    if any(item["status"] != WAITING for item in WAITING_LIST):
        problems.append("something did not wait for a person")
    if refunds and "approv" not in answer.lower():
        problems.append("did not tell the customer that a person approves the refund")
    if answer == HANDOFF:
        problems.append("stopped by a limit")
    return problems, lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai", "claude"], default="openai")
    options = parser.parse_args()

    passed, tokens = 0, 0
    for number, case in enumerate(CASES, start=1):
        WAITING_LIST.clear()  # every case starts with an empty waiting list
        with redirect_stdout(io.StringIO()):  # keep the screen short: only the results
            answer, trace = run(case["message"], options.provider)
        problems, lines = check(case, answer, trace)
        tokens += sum((line["input_tokens"] or 0) + (line["output_tokens"] or 0) for line in lines)
        if problems:
            print(f"FAIL {number:2} {case['name']}: {'; '.join(problems)}")
            print(f"        agent: {answer}")
        else:
            passed += 1
            print(f"PASS {number:2} {case['name']}")
    print(f"\n{passed} of {len(CASES)} cases passed · {tokens:,} tokens in total")
