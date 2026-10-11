"""Count the failure categories in labels.jsonl, and show when the last new category appeared.

    uv run python sessions/4.3-error-analysis/count_labels.py
"""
import json
from collections import Counter
from pathlib import Path

labels = [json.loads(line) for line in (Path(__file__).parent / "labels.jsonl").read_text().splitlines()]

failed = [label for label in labels if not label["ok"]]
print(f"{len(labels)} traces read, {len(failed)} failed, {len(labels) - len(failed)} passed\n")

print("Failure categories:")
for category, count in Counter(label["category"] for label in failed).most_common():
    traces = [label["n"] for label in failed if label["category"] == category]
    print(f"  {count:>2}  {category:<30} traces {traces}")

caught = [label["n"] for label in labels if label["caught_by_tool"]]
print(f"\nCaught by a tool before the customer saw it: {len(caught)} traces {caught}")

# Saturation: in reading order, when did each category appear for the first time?
print("\nNew categories, in reading order:")
seen = set()
for label in labels:
    if label["category"] and label["category"] not in seen:
        seen.add(label["category"])
        last_new = label["n"]
        print(f"  trace {label['n']:>2}: {label['category']}")
print(f"  traces {last_new + 1} to {len(labels)}: no new category")
