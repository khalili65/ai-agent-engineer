"""Step 5c: a person reads every facts_judge FAIL. The verdicts are in results/<name>_facts_review.csv.

    uv run python labs/02-evals/review.py v1
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent

if __name__ == "__main__":
    name = sys.argv[1]
    runs = len((HERE / "results" / f"{name}.jsonl").read_text().splitlines())
    rows = list(csv.DictReader((HERE / "results" / f"{name}_facts_review.csv").open()))
    real = [r for r in rows if r["person"] == "real"]
    print(f"{name}: facts_judge did not pass {len(rows)} of {runs} runs. A person read all {len(rows)}:")
    print(f"  real fact errors   {len(real):3}")
    print(f"  false alarms       {len(rows) - len(real):3}")
    print(f"facts, checked by a person: {runs - len(real)} of {runs} runs right = {(runs - len(real)) / runs:.0%}")
