"""Check the dataset before we trust it.

    uv run python sessions/4.4-first-dataset/check_cases.py

1. Every line has the five fields, and every id is new.
2. Every amount and fee is worked out again from Daniel's rules (the code in tools.py).
3. Count the cases by source and by tag.
"""
import json
import re
from collections import Counter
from pathlib import Path

from support_agent_v1 import BOOKINGS, change_fee, refund_amount

HERE = Path(__file__).parent
FIELDS = ["id", "message", "expected", "tags", "source"]
EXPECTED_KEYS = {"tool", "refund", "amount", "fee", "no_promise"}

cases = [json.loads(line) for line in (HERE / "cases.jsonl").read_text().splitlines()]
problems, seen, checked = [], set(), 0

for case in cases:
    # 1. The shape of the line.
    if list(case) != FIELDS:
        problems.append(f"{case.get('id')}: the fields must be {FIELDS}")
    if case["id"] in seen:
        problems.append(f"{case['id']}: this id is used twice")
    seen.add(case["id"])
    if not set(case["expected"]) <= EXPECTED_KEYS:
        problems.append(f"{case['id']}: unknown key in expected {case['expected']}")
    if not re.fullmatch(r"trace:\w+|written|synthetic", case["source"]):
        problems.append(f"{case['id']}: unknown source {case['source']}")

    # 2. Amounts and fees, worked out again from the rules.
    ids = [b.upper() for b in re.findall(r"NT-\d+", case["message"], re.I) if b.upper() in BOOKINGS]
    expected = case["expected"]
    if "amount" in expected:
        reason = "airline_cancelled" if "airline_cancelled" in case["tags"] else "changed_mind"
        allowed = [refund_amount(BOOKINGS[b], reason) for b in ids]
        checked += 1
        if expected["amount"] not in allowed:
            problems.append(f"{case['id']}: amount {expected['amount']}, but the rules say {allowed}")
    if "fee" in expected:
        fees = [change_fee(BOOKINGS[b]) for b in ids]
        checked += 1
        if expected["fee"] not in fees:
            problems.append(f"{case['id']}: fee {expected['fee']}, but the rules say {fees}")

print(f"{len(cases)} cases · {checked} amounts and fees worked out again from the rules")
for p in problems:
    print("PROBLEM", p)
print(f"{len(problems)} problems\n")

sources = Counter(c["source"].split(":")[0] for c in cases)
print("By source:", ", ".join(f"{k} {v}" for k, v in sources.most_common()))
tags = Counter(t for c in cases for t in c["tags"])
print("By tag:   ", ", ".join(f"{k} {v}" for k, v in tags.most_common()))
