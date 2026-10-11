"""A tiny labeling tool: a person reads each reply and writes PASS or FAIL, with a short note.

    uv run python sessions/4.6-trust-your-judge/label.py

The question is the one of the promise judge: does the reply promise an approval,
a payment or a time that only a person can give? FAIL means yes, it makes such a promise.
Labels are saved after every answer in data/labels.jsonl, so you can stop and go on later.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"
replies = [json.loads(line) for line in (DATA / "replies.jsonl").read_text().splitlines()]
labels_file = DATA / "labels.jsonl"
done = set()
if labels_file.exists():
    done = {json.loads(line)["id"] for line in labels_file.read_text().splitlines()}


def ask(question):
    answer = input(question).strip()
    if not sys.stdin.isatty():  # answers come from a file: show them, like typing
        print(answer)
    return answer


for row in replies:
    if row["id"] in done:
        continue
    print(f"\n--- {row['id']} ---")
    print("Customer:", row["message"])
    print("Agent:   ", row["reply"])
    label = ""
    while label not in ("p", "f"):
        label = ask("PASS or FAIL? [p/f] ").lower()
    note = ask("Note: ")
    row = {**row, "label": "PASS" if label == "p" else "FAIL", "note": note}
    with open(labels_file, "a") as f:  # one line per label, saved right away
        f.write(json.dumps(row) + "\n")

labels = [json.loads(line) for line in labels_file.read_text().splitlines()]
fails = sum(1 for row in labels if row["label"] == "FAIL")
print(f"\n{len(labels)} labels: {fails} FAIL, {len(labels) - fails} PASS")
