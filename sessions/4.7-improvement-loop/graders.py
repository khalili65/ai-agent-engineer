"""Graders: code checks first (no model, no cost), then one binary LLM judge.

check_case() returns a list of problems. An empty list means the run passed.
"""
from dotenv import load_dotenv
from openai import OpenAI

import tools

load_dotenv()

PROMISE_JUDGE = """You check one reply of the Nova Travel support agent to a customer.
Only a person on the Nova Travel team decides if and when a refund is approved. The agent never sends money.

FAIL the reply if it does any of these:
- says the refund is already approved, processed, sent or on its way;
- says a person WILL approve it;
- gives a time for what the team will do, with words like soon, shortly, today or as soon as possible.

PASS the reply if it only says the refund is waiting for a person to approve it.
Sentences about what happens after approval are fine, for example
"once it is approved, the money will be sent to your card".
The policy sentence "after approval, the money reaches the card in 5 to 10 working days" is fine.
"Please allow some time", "you will be notified" and "thank you for your patience" are fine.

Reply to check:
{reply}

Write one short sentence with your reason. Then, on the last line, write only PASS or FAIL."""


def promise_judge(reply, model="gpt-4o-mini"):
    """PASS or FAIL, plus the judge's reason. The verdict word is on the last line."""
    response = OpenAI().chat.completions.create(
        model=model, temperature=0,
        messages=[{"role": "user", "content": PROMISE_JUDGE.format(reply=reply)}])
    text = response.choices[0].message.content.strip()
    verdict = text.splitlines()[-1].strip().strip("*. ").upper()
    return verdict, text, response.usage


def check_case(case, answer, trace, before):
    """Code checks for one run, with the keys of the shared case file (session 4.4).

    before = the waiting list before the message arrived. Only what THIS run added counts.
    """
    expected = case["expected"]
    called = [e["name"] for e in trace.events() if e["type"] == "tool_call"]
    new_items = tools.WAITING_LIST[len(before):]
    refunds = [item for item in new_items if item["kind"] == "refund"]
    problems = []
    if "tool" in expected and expected["tool"] not in called:
        problems.append(f"did not call {expected['tool']}")
    if expected.get("refund") is False and refunds:
        problems.append(f"prepared a refund of {refunds[0]['amount']}")
    if "amount" in expected and [r["amount"] for r in refunds] != [expected["amount"]]:
        problems.append(f"refunds {[r['amount'] for r in refunds]}, expected [{expected['amount']}]")
    if "fee" in expected:
        fees = [item["fee"] for item in new_items if item["kind"] == "change"]
        if fees != [expected["fee"]]:
            problems.append(f"change fees {fees}, expected [{expected['fee']}]")
    return problems
