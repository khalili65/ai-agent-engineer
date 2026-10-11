"""Run the support agent v1 once on every case, with simple code checks: the first baseline.

    uv run python sessions/4.4-first-dataset/run_baseline.py

Every run writes a trace to traces/traces.jsonl. The results go to results/baseline.jsonl.
"""
import io
import json
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

from support_agent_v1 import WAITING, WAITING_LIST, run

HERE = Path(__file__).parent
# A rough word check for promises. Session 4.5 builds a real judge for this.
PROMISE_WORDS = ["soon", "shortly", "will be approved", "i will notify"]


def check(expected, answer, called):
    """Return a list of problems, each with its kind. An empty list means the case passed."""
    refunds = [item["amount"] for item in WAITING_LIST if item["kind"] == "refund"]
    fees = [item["fee"] for item in WAITING_LIST if item["kind"] == "change"]
    problems = []
    if "tool" in expected and expected["tool"] not in called:
        problems.append(("tool", f"did not call {expected['tool']}"))
    if "amount" in expected and refunds != [expected["amount"]]:
        problems.append(("amount", f"refunds {refunds}, expected [{expected['amount']}]"))
    if expected.get("refund") is False and refunds:
        problems.append(("refund", f"prepared a refund of {refunds[0]}, expected none"))
    if "fee" in expected and fees != [expected["fee"]]:
        problems.append(("fee", f"change fees {fees}, expected [{expected['fee']}]"))
    if any(item["status"] != WAITING for item in WAITING_LIST):
        problems.append(("money", "something did not wait for a person"))  # no money may ever move
    if expected.get("no_promise"):
        words = [w for w in PROMISE_WORDS if w in answer.lower()]
        if words:
            problems.append(("promise", f"promise words: {', '.join(words)}"))
    return problems


if __name__ == "__main__":
    cases = [json.loads(line) for line in (HERE / "cases.jsonl").read_text().splitlines()]
    results, passed = [], 0
    for case in cases:
        WAITING_LIST.clear()  # every case starts with an empty waiting list
        with redirect_stdout(io.StringIO()):  # keep the screen short
            answer, trace = run(case["message"])
        called = [e["name"] for e in trace.events() if e["type"] == "tool_call"]
        problems = check(case["expected"], answer, called)
        passed += not problems
        results.append({"id": case["id"], "run_id": trace.run_id, "passed": not problems,
                        "problems": problems, "answer": answer, "source": case["source"],
                        "tags": case["tags"]})
        print(f"{'PASS' if not problems else 'FAIL'} {case['id']}  {'; '.join(text for _, text in problems)}")

    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "baseline.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"\nBaseline: {passed} of {len(cases)} cases passed ({passed / len(cases):.0%})")
    for source in ["trace", "written", "synthetic"]:
        group = [r for r in results if r["source"].split(":")[0] == source]
        print(f"  {source:<10} {sum(r['passed'] for r in group)} of {len(group)}")
    kinds = Counter(kind for r in results for kind, _ in r["problems"])
    print("Failed checks:", ", ".join(f"{k} {v}" for k, v in kinds.most_common()))
