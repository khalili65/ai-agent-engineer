"""Step 5b: compare two eval runs, grade by grade and case by case.

    uv run python labs/02-evals/compare.py v1 v2
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from gate import GRADES, summary

HERE = Path(__file__).parent


def load(name):
    return [json.loads(line) for line in (HERE / "results" / f"{name}.jsonl").read_text().splitlines()]


def per_case(rows):
    """case id -> grade -> (passed, runs)"""
    table = defaultdict(lambda: {g: [0, 0] for g in GRADES})
    for r in rows:
        for g in GRADES:
            table[r["case"]][g][0] += r[g] == "PASS"
            table[r["case"]][g][1] += 1
    return table


if __name__ == "__main__":
    before, after = sys.argv[1], sys.argv[2]
    a, b = load(before), load(after)
    ra, rb = summary(a), summary(b)
    print(f"{'':10}{before:>8}{after:>8}")
    for grade in GRADES + ["all"]:
        print(f"{grade:10}{ra[grade]:8.0%}{rb[grade]:8.0%}")
    ca, cb = per_case(a), per_case(b)
    print("\nCases that changed by 2 or more runs (a change of 1 run is often just noise):")
    for case in sorted(ca):
        moved = [g for g in GRADES if abs(cb[case][g][0] - ca[case][g][0]) >= 2]
        if moved:
            ups = [g for g in moved if cb[case][g][0] > ca[case][g][0]]
            label = "better" if len(ups) == len(moved) else "worse " if not ups else "mixed "
            changes = [f"{g} {ca[case][g][0]}/{ca[case][g][1]} -> {cb[case][g][0]}/{cb[case][g][1]}" for g in moved]
            print(f"  {case}  {label}  {' · '.join(changes)}")
