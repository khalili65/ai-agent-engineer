"""Run every task several times (trials) and grade the outcome with code.

    uv run python sessions/4.1-why-evals/trials.py            # 5 trials per task
    uv run python sessions/4.1-why-evals/trials.py 3          # 3 trials per task

The grader here is code: it looks at the outcome (the waiting list after the run),
not at the words of the reply. Every reply is saved too, so a person can read them.
"""
import json
import sys

from tasks import HERE, TASKS, run_task

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def grade_outcome(task, waiting):
    """Code grader: are exactly the expected refunds on the waiting list?"""
    refunds = [item["amount"] for item in waiting if item["kind"] == "refund"]
    return refunds == task["expected_refunds"], refunds


results = []
for task in TASKS:
    print(f"Task {task['id']}: expected refunds {task['expected_refunds']}")
    passed = 0
    for trial in range(1, TRIALS + 1):
        reply, trace, waiting = run_task(task)
        ok, refunds = grade_outcome(task, waiting)
        passed += ok
        tools = [line["name"] for line in trace.events() if line["type"] == "tool_call"]
        print(f"  trial {trial} · run {trace.run_id} · {'PASS' if ok else 'FAIL'} · refunds {refunds}")
        results.append({"task": task["id"], "trial": trial, "run_id": trace.run_id,
                        "tools": tools, "refunds": refunds, "pass": ok, "reply": reply})
    print(f"  {passed} of {TRIALS} trials passed\n")

with open(HERE / "results.jsonl", "w") as f:  # one line per trial, every reply included
    for row in results:
        f.write(json.dumps(row) + "\n")
print(f"{sum(r['pass'] for r in results)} of {len(results)} trials passed · replies in results.jsonl")
