"""Session 4.5, step 3: the human review sheet for Daniel.

    uv run python sessions/4.5-graders/review_sample.py

Every reply that a judge failed, plus five random replies that both judges passed.
Daniel writes his own PASS or FAIL in the two empty columns.
"""
import csv
import json
import random

from traces import HERE

rows = [json.loads(line) for line in (HERE / "judged.jsonl").read_text().splitlines()]
failed = [r for r in rows if r["promise"] != "PASS" or r["facts"] != "PASS"]
passed = [r for r in rows if r not in failed]
random.seed(1)  # the same sample every time we run it
sample = failed + random.sample(passed, 5)

with open(HERE / "review_sheet.csv", "w", newline="") as f:
    sheet = csv.writer(f)
    sheet.writerow(["run_id", "case", "reply", "promise_judge", "facts_judge",
                    "daniel_promise", "daniel_facts", "note"])
    for r in sample:
        sheet.writerow([r["run_id"], r["case"], r["reply"], r["promise"], r["facts"], "", "", ""])
        print(f"{r['run_id']}  {r['case']}  promise {r['promise']}  facts {r['facts']}")
print(f"\n{len(failed)} failed + 5 random passed = {len(sample)} replies for Daniel, in review_sheet.csv")
