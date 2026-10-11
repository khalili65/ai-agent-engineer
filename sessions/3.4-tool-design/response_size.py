"""Session 3.4: the same tools v2, but find_booking returns the raw record or the short one.

Run:  uv run python sessions/3.4-tool-design/response_size.py detailed
      uv run python sessions/3.4-tool-design/response_size.py concise
"""
import json
import re
import sys
import tiktoken
import tools_v2
from agent import run_agent

MODE = sys.argv[1] if len(sys.argv) > 1 else "concise"
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
tools_v2.DETAILED = MODE == "detailed"

# How big is one answer of find_booking? (o200k_base is the tokenizer of gpt-4o-mini)
encoding = tiktoken.get_encoding("o200k_base")
sara = json.dumps(tools_v2.find_booking("NT-4821"))
print(f"find_booking('NT-4821') in {MODE} mode: {len(encoding.encode(sara)):,} tokens")

TESTS = [
    ("John: price", r"\b380\b", "Hi, this is John. How much did I pay for my Rome trip? Booking NT-5107."),
    ("Sara: flight", r"\bcancell?ed\b", "hello, is my flight to Lisbon still happening? my booking is nt 4821"),
    ("Lukas: dates", r"(12|twelfth).*(16|sixteenth)",
     "This is Lukas. What are the dates of my Paris trip? The booking number is 6190."),
    ("Sara: refund", None, "The airline cancelled my flight to Lisbon. Booking NT-4821. "
                           "Please give me my money back."),
]

right, tokens = 0, 0
for name, fact, message in TESTS:
    print(f"== {name} ==")
    for run in range(1, RUNS + 1):
        tools_v2.WAITING_LIST.clear()
        out = run_agent(message, tools_v2.TOOLS, tools_v2.FUNCTIONS,
                        run_id=f"{MODE}-{name}-{run}", trace_file=f"size_{MODE}.jsonl")
        if fact:
            ok = bool(re.search(fact, out["answer"], re.I | re.S))
        else:  # the refund request on Daniel's list: NT-4821, 640 dollars
            ok = any(r["booking_id"] == "NT-4821" and r["amount"] == 640
                     for r in tools_v2.WAITING_LIST)
        right += ok
        tokens += out["input_tokens"]
        print(f"  run {run}: {'RIGHT' if ok else 'WRONG'} {out['input_tokens']:,} input tokens | "
              f"{out['answer'][:110]}")

n = len(TESTS) * RUNS
print(f"\n{MODE}: {right} of {n} right | {tokens:,} input tokens | "
      f"{tokens // n:,} input tokens per conversation")
