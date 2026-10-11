"""Split the labeled replies into three groups: train, dev and test.

    uv run python sessions/4.6-trust-your-judge/split.py

train (20%): we may read these and copy them into the judge prompt as examples.
dev   (40%): we measure the judge here, again and again, while we improve the prompt.
test  (40%): we measure the final judge here only once, at the very end.
Each group gets the same share of FAIL labels, so every group has some failures.
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).parent / "data"
labels = [json.loads(line) for line in (DATA / "labels.jsonl").read_text().splitlines()]

random.seed(7)  # the same split every time we run the file
groups = {"train": [], "dev": [], "test": []}
for label in ("FAIL", "PASS"):
    rows = [row for row in labels if row["label"] == label]
    random.shuffle(rows)
    n_train, n_dev = round(len(rows) * 0.2), round(len(rows) * 0.4)
    groups["train"] += rows[:n_train]
    groups["dev"] += rows[n_train:n_train + n_dev]
    groups["test"] += rows[n_train + n_dev:]

for name, rows in groups.items():
    rows.sort(key=lambda row: row["id"])
    with open(DATA / f"{name}.jsonl", "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    fails = sum(1 for row in rows if row["label"] == "FAIL")
    print(f"{name:5}  {len(rows):2} replies  {fails} FAIL  {len(rows) - fails:2} PASS")
