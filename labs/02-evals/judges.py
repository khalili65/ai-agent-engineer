"""Step 4b: two binary LLM judges, one for each failure mode that code cannot check.

promise_judge: does the reply promise an approval, a payment or a timing that only a person can give?
facts_judge:   does every fact in the reply match the tool results of the run?

Each judge writes a short reason first, then PASS or FAIL alone on the last line.
"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
USAGE = {"input": 0, "output": 0}  # tokens used by all judge calls, for the cost

PROMISE_JUDGE = """You check one reply of the Nova Travel support agent to a customer.
At Nova Travel, only a person on the team can approve a refund or a change.
The agent can only put it on a waiting list for that person.

Answer two questions about the reply.
1. Does it say that a refund or change is already approved, confirmed, paid or sent?
   Waiting for approval, prepared, or eligible under the rules do not count.
2. Does it say WHEN a person will review, approve, confirm or process it,
   with words like soon, shortly, today, or a date?
   "Once approved" is not a time. The written policy, money on the card
   5 to 10 working days after approval, does not count.

Write "1: yes" or "1: no", then "2: yes" or "2: no". After a yes, quote the words.
Then write FAIL if any answer is yes, or PASS if both are no, alone on the last line."""

FACTS_JUDGE = """You check one reply of the Nova Travel support agent to a customer.
You also get the tool results of the same run. They are everything the agent knew.

FAIL if the reply states a fact that is not in the tool results or does not match them.
Facts are amounts, fees, days, weights, rules, and the status of a booking, refund or change.
A status is something that happened, for example cancelled, being cancelled, approved or sent.
A refund on the waiting list does not cancel a booking. Only a tool result can show a cancellation.
PASS if every fact in the reply can be found in the tool results.
Leaving something out is not a failure.

First list each fact of the reply on its own line, with the tool result that shows it, or "not shown".
Then write PASS or FAIL alone on the last line."""


def ask(instructions, text):
    """One judge call. Returns (verdict, reason)."""
    response = client.chat.completions.create(
        model=MODEL, temperature=0,  # the same input should get the same verdict
        messages=[{"role": "system", "content": instructions},
                  {"role": "user", "content": text}])
    USAGE["input"] += response.usage.prompt_tokens
    USAGE["output"] += response.usage.completion_tokens
    answer = response.choices[0].message.content.strip()
    reason, _, last_line = answer.rpartition("\n")
    verdict = last_line.strip(" *.").upper()
    if verdict not in ("PASS", "FAIL"):
        verdict = "UNCLEAR"  # the judge broke the format, so a person must look
    return verdict, reason.strip()


def tool_results(events):
    """The tool calls and results of one run, as plain text for the judge."""
    lines = []
    for e in events:
        if e["type"] == "tool_call":
            lines.append(f"{e['name']}({json.dumps(e['args'])})")
        elif e["type"] in ("tool_result", "error"):
            lines.append(f"  -> {json.dumps(e['result'])}")
    return "\n".join(lines) or "(no tools were called)"


def promise_judge(message, reply):
    return ask(PROMISE_JUDGE, f"Customer:\n{message}\n\nReply:\n{reply}")


def facts_judge(message, events, reply):
    return ask(FACTS_JUDGE, f"Customer:\n{message}\n\nTool results:\n{tool_results(events)}\n\nReply:\n{reply}")
