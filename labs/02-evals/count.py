"""Step 2b: count the failure categories in notes.csv.

    uv run python labs/02-evals/count.py
"""
import csv
from collections import Counter
from pathlib import Path

rows = list(csv.DictReader((Path(__file__).parent / "notes.csv").open()))
failed = [row for row in rows if row["category"]]
print(f"{len(rows)} runs read · {len(failed)} with a failure · {len(rows) - len(failed)} good\n")
for category, count in Counter(row["category"] for row in failed).most_common():
    where = Counter(row["first_failure"].split(" ", 2)[2] for row in failed if row["category"] == category)
    places = ", ".join(f"{name} {n}" for name, n in where.items())
    print(f"{count:3}  {count / len(rows):4.0%}  {category:32} first failure at: {places}")
