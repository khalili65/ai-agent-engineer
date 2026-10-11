"""Add the synthetic candidates that a person kept to cases.jsonl.

    uv run python sessions/4.4-first-dataset/add_synthetic.py

synthetic_review.jsonl holds one decision per candidate: keep true or false, and why.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
TAGS = {"changed_mind": ["refund", "changed_mind"], "airline_cancelled": ["refund", "airline_cancelled"],
        "change_dates": ["change"], "refund_status": ["refund_status"], "baggage": ["baggage"],
        "14_days": ["edge_14_days"], "15_days": ["edge_15_days"], "typo_in_id": ["typo_in_id"]}


def read(name):
    return [json.loads(line) for line in (HERE / name).read_text().splitlines()]


candidates = read("synthetic_candidates.jsonl")
review = {r["candidate"]: r for r in read("synthetic_review.jsonl")}
cases = read("cases.jsonl")
if any(c["source"] == "synthetic" for c in cases):
    raise SystemExit("The synthetic cases are already in cases.jsonl.")

kept = [c for c in candidates if review[c["candidate"]]["keep"]]
for c in candidates:
    if not review[c["candidate"]]["keep"]:
        print(f"rejected {c['candidate']}: {review[c['candidate']]['why']}")

with open(HERE / "cases.jsonl", "a") as f:
    for number, c in enumerate(kept, start=len(cases) + 1):
        tags = [t for tag in c["tags"] for t in TAGS[tag]]
        case = {"id": f"c{number:02}", "message": c["message"], "expected": c["expected"],
                "tags": tags, "source": "synthetic"}
        f.write(json.dumps(case) + "\n")

print(f"\n{len(candidates)} candidates · {len(kept)} kept · {len(candidates) - len(kept)} rejected")
print(f"cases.jsonl now has {len(cases) + len(kept)} cases")
