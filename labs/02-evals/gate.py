"""Step 6: the eval gate. It reads one results file and stops a change that makes the agent worse.

    uv run python labs/02-evals/gate.py v2        # reads results/v2.jsonl

Exit code 0 means every grade reached its bar. Exit code 1 means at least one did not,
so a CI system (for example GitHub Actions) marks the run as failed.
"""
import json
import sys
from pathlib import Path

GRADES = ["code", "promise", "facts"]

# The bars: a little below what the fixed agent reached, so normal noise passes,
# but a real step back fails. facts_judge has no bar: it is a warning, and a person reads its FAILs.
BARS = {"code": 0.80, "promise": 0.90}


def summary(rows):
    """Share of runs that passed each grade, and all three together."""
    total = len(rows)
    rates = {g: sum(r[g] == "PASS" for r in rows) / total for g in GRADES}
    rates["all"] = sum(all(r[g] == "PASS" for g in GRADES) for r in rows) / total
    return rates


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "latest"
    path = Path(__file__).parent / "results" / f"{name}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rates = summary(rows)
    failed = []
    print(f"Eval gate · results/{name}.jsonl · {len(rows)} runs")
    for grade, bar in BARS.items():
        ok = rates[grade] >= bar
        print(f"  {'PASS' if ok else 'FAIL'}  {grade:8} {rates[grade]:5.0%}   bar {bar:.0%}")
        if not ok:
            failed.append(grade)
    print(f"  note  facts    {rates['facts']:5.0%}   no bar: a person reads the facts_judge FAILs")
    if failed:
        print(f"Gate closed: {', '.join(failed)} below the bar.")
        sys.exit(1)
    print("Gate open: every grade reached its bar.")
