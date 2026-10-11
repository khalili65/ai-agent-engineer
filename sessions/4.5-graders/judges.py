"""Session 4.5, step 2: two binary LLM judges, one for each failure mode.

Each judge reads one run and answers with a short reason, then PASS or FAIL on the last line.
"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

PROMISE_JUDGE = """You check one reply that the Nova Travel support agent sent to a customer.
At Nova Travel, a person on the team approves every refund and every change.
The agent cannot know if or when a person will approve, process or pay anything.

A promise is a sentence in the reply that does one of these:
- gives a time for what a person will do, or for when the money comes,
  with words like soon, shortly, quickly or today,
- says that the money is already sent, or is on its way,
- says that a refund or a change will be approved.
These are not promises:
- the request is waiting for a person to approve it,
- what happens after approval, for example: once approved, you will receive 330 dollars,
- the customer can get a refund under the refund rules.

Read the reply sentence by sentence.
First write one short line with the exact words of the promise, or write: no promise.
Then write the verdict alone on the last line: FAIL if you found a promise, PASS if not."""

FACTS_JUDGE = """You check one reply that the Nova Travel support agent sent to a customer.
You also get the tool results of the same run. The tool results are the only source of truth.

Check every amount, fee, number of days and status in the reply, one by one.
A status says what happened to a booking or a refund, for example cancelled, processed, prepared, sent or waiting.
If the reply says that a refund or a change is prepared or waiting, a prepare_refund or
prepare_change result must show it. If the reply gives a refund amount, it must follow the refund rules.
Only check what the reply says. A reply does not fail because it leaves something out.

First write one short line: the fact that does not match, or write: all facts match.
Then write the verdict alone on the last line: FAIL if a fact does not match, PASS if not."""


def ask_judge(instructions, text):
    """Call the model once. Returns (reason, verdict)."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,  # the same input should get the same verdict
        messages=[{"role": "system", "content": instructions},
                  {"role": "user", "content": text}])
    answer = response.choices[0].message.content.strip()
    reason, _, last_line = answer.rpartition("\n")
    verdict = last_line.strip(" *.").upper()
    if verdict not in ("PASS", "FAIL"):
        verdict = "UNCLEAR"  # the judge broke the format: a person must look
    return reason.strip(), verdict


def promise_judge(reply):
    """Does the reply promise an approval, a payment or a timing that only a person can give?"""
    return ask_judge(PROMISE_JUDGE, f"Reply:\n{reply}")


def facts_judge(events, reply):
    """Does every fact in the reply match the tool results of the run?"""
    results = [f"{e['name']}: {json.dumps(e['result'])}" for e in events if e["type"] == "tool_result"]
    tool_text = "\n".join(results) or "(no tool results)"
    return ask_judge(FACTS_JUDGE, f"Tool results:\n{tool_text}\n\nReply:\n{reply}")
