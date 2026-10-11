"""Session 4.5, step 2: run both judges on the final reply of every run.

    uv run python sessions/4.5-graders/run_judges.py

The verdicts are saved in judged.jsonl, for the human review.
"""
import json

from judges import facts_judge, promise_judge
from traces import HERE, customer_message, final_reply, load_cases, load_runs

cases = load_cases()
saved = []
for run_id, events in load_runs().items():
    case = cases[customer_message(events)]
    reply = final_reply(events)
    promise_reason, promise = promise_judge(reply)
    facts_reason, facts = facts_judge(events, reply)
    print(f"{run_id}  {case['id']}  promise {promise}  facts {facts}")
    for name, verdict, reason in [("promise", promise, promise_reason), ("facts", facts, facts_reason)]:
        if verdict != "PASS":
            print(f"    {name}: {reason}")
    saved.append({"run_id": run_id, "case": case["id"], "reply": reply,
                  "promise": promise, "promise_reason": promise_reason,
                  "facts": facts, "facts_reason": facts_reason})

with open(HERE / "judged.jsonl", "w") as f:
    for row in saved:
        f.write(json.dumps(row) + "\n")
fails = sum(r["promise"] != "PASS" or r["facts"] != "PASS" for r in saved)
print(f"\n{len(saved)} replies judged, {fails} failed at least one judge.")
