"""Check the promise judge against 20 replies that we labeled by hand.

    uv run python sessions/4.7-improvement-loop/check_judge.py
"""
import json
from pathlib import Path

from graders import promise_judge

labels = [json.loads(line) for line in
          (Path(__file__).parent / "suites" / "promise_labels.jsonl").read_text().splitlines()]
agree = 0
for row in labels:
    verdict, reason, _ = promise_judge(row["reply"])
    if verdict == row["label"]:
        agree += 1
    else:
        print(f"DISAGREE run {row['run_id']}: we said {row['label']}, judge said {verdict}")
        print(f"         reply: {row['reply']}")
print(f"\njudge agrees with our labels on {agree} of {len(labels)} replies")
