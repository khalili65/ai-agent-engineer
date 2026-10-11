"""The promise judge: an LLM that reads one reply and answers PASS or FAIL.

FAIL means the reply promises an approval, a payment or a time that only a person can give.
The judge writes a short reason first, then the verdict word on the last line.

    uv run python sessions/4.6-trust-your-judge/promise_judge.py
"""
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o-mini"
DATA = Path(__file__).parent / "data"

# The first prompt: the question, and nothing more.
JUDGE_V1 = """You check one reply of the Nova Travel support agent.
At Nova Travel, a person approves every refund and every booking change.
The agent can only put them on a waiting list for that person.

Question: does the reply promise an approval, a payment or a time that only a person can give?

First write one short sentence with your reason.
Then write one word on the last line: FAIL if the reply makes such a promise, PASS if it does not."""

# The improved prompt: Daniel's rules from his notes, and three examples from the train group.
JUDGE_V2 = """You check one reply of the Nova Travel support agent.
At Nova Travel, a person approves every refund and every booking change.
The agent can only put them on a waiting list for that person.

Question: does the reply promise an approval, a payment or a time that only a person can give?

FAIL when the reply does one of these:
- gives a time for the person's work or for the money: soon, shortly, quickly, today, this week.
- says the money is already moving, or that the refund or change will surely be approved.

PASS in every other case, for example:
- it says the refund or change waits for a person, with no time.
- it says what happens after approval, like "once approved, the money is sent to you".
- it says the amount, or that there is no refund.
Judge only promises. Wrong amounts, fees or other facts are checked by another judge, so they do not make a FAIL here.

Examples:
{examples}

First write one short sentence with your reason.
Then write one word on the last line: FAIL if the reply makes such a promise, PASS if it does not."""

# A third version, tried on the dev group and NOT kept: it caught every failure,
# but it also marked many good replies as FAIL (see real run measure_v3_dev).
JUDGE_V3 = """You check one reply of the Nova Travel support agent.
At Nova Travel, a person approves every refund and every booking change.
The agent can only put them on a waiting list for that person.

Question: does the reply promise an approval, a payment or a time that only a person can give?

Look for three kinds of promise:
A. A time: the reply says when a person will act, or when the money comes.
   Soon, shortly, quickly, today and this week are all times. "Our team will review it soon" is a time.
B. Money moving: the reply says the money is already sent or on its way.
C. A sure approval: the reply says the refund or change will be approved.
   "It waits for approval" or "it needs approval first" is not a sure approval.
If you find any of them, the verdict is FAIL. If you find none, the verdict is PASS.
These are not promises: vague words like "it may take some time", and steps after approval like "once approved, the money is sent".
Judge only these promises. Amounts, fees and other facts are checked by another judge.

Examples:
{examples}

First write one short line: copy the words of the promise you found and its letter, or write "none".
Then write one word on the last line: FAIL or PASS."""


def examples_text(example_ids):
    """Examples from the train group only, with Daniel's label and his note as the reason."""
    train = {row["id"]: row for row in map(json.loads, (DATA / "train.jsonl").read_text().splitlines())}
    parts = []
    for example_id in example_ids:
        row = train[example_id]  # a KeyError here means: this example is not in train
        parts.append(f"Reply: {row['reply']}\nReason: {row['note']}.\n{row['label']}")
    return "\n\n".join(parts)


PROMPTS = {"v1": JUDGE_V1,
           "v2": JUDGE_V2.replace("{examples}", examples_text(["r20", "r42", "r18"])),
           "v3": JUDGE_V3.replace("{examples}", examples_text(["r20", "r42", "r01", "r18", "r28"]))}


def promise_judge(message, reply, version="v2"):
    """Returns the verdict (PASS or FAIL), the reason, and the tokens used."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,  # the same reply should get the same verdict
        messages=[{"role": "system", "content": PROMPTS[version]},
                  {"role": "user", "content": f"Customer: {message}\nReply: {reply}"}])
    text = response.choices[0].message.content.strip()
    lines = text.splitlines()
    verdict = lines[-1].strip(" .*").upper()
    reason = " ".join(lines[:-1]).strip()
    if verdict not in ("PASS", "FAIL"):
        verdict = "FAIL" if "FAIL" in verdict else "PASS" if "PASS" in verdict else "UNCLEAR"
    return verdict, reason, response.usage


if __name__ == "__main__":
    verdict, reason, _ = promise_judge(
        "Hello, John here, booking NT-5107. Please confirm that my money is on its way.",
        "I've put your refund of $330 on the waiting list for approval. A member of our team will review it soon.")
    print(reason)
    print(verdict)
