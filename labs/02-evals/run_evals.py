"""Step 5: run the agent on every case, several times, and grade every run.

    uv run python labs/02-evals/run_evals.py --name v1
    uv run python labs/02-evals/run_evals.py --name v2 --trials 3

Each run gets three grades: the code checks, promise_judge and facts_judge.
Results: results/<name>.jsonl (one line per run) and the traces in results/<name>_traces/.
"""
import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "agent"))

import trace_log  # noqa: E402
from agent import run  # noqa: E402
from checks import check_case  # noqa: E402
from gate import GRADES, summary  # noqa: E402
from judges import USAGE, facts_judge, promise_judge  # noqa: E402
from tools import WAITING_LIST  # noqa: E402


def grade_one(case):
    """Run the agent once on one case and grade the run."""
    WAITING_LIST.clear()
    with redirect_stdout(io.StringIO()):
        reply, trace = run(case["message"])
    events = trace.events()
    problems = check_case(case, WAITING_LIST, events)
    promise, promise_reason = promise_judge(case["message"], reply)
    facts, facts_reason = facts_judge(case["message"], events, reply)
    tokens_in = sum(e["input_tokens"] or 0 for e in events)
    tokens_out = sum(e["output_tokens"] or 0 for e in events)
    return {"case": case["id"], "run_id": trace.run_id, "reply": reply,
            "tokens_in": tokens_in, "tokens_out": tokens_out,
            "code": "FAIL" if problems else "PASS", "problems": problems,
            "promise": promise, "promise_reason": promise_reason,
            "facts": facts, "facts_reason": facts_reason}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="latest")
    parser.add_argument("--trials", type=int, default=3)
    options = parser.parse_args()

    out = HERE / "results" / f"{options.name}.jsonl"
    out.parent.mkdir(exist_ok=True)
    trace_log.TRACE_DIR = HERE / "results" / f"{options.name}_traces"
    (trace_log.TRACE_DIR / "traces.jsonl").unlink(missing_ok=True)
    cases = [json.loads(line) for line in (HERE / "cases.jsonl").read_text().splitlines()]

    rows = []
    with out.open("w") as f:
        for case in cases:
            results = [grade_one(case) for _ in range(options.trials)]
            for row in results:
                f.write(json.dumps(row) + "\n")
            rows += results
            marks = "  ".join(f"{g} {sum(r[g] == 'PASS' for r in results)}/{len(results)}" for g in GRADES)
            print(f"{case['id']}  {marks}  {', '.join(case['tags'])}")

    rates = summary(rows)
    print(f"\n{len(rows)} runs ({len(cases)} cases x {options.trials} trials) · {out.relative_to(HERE)}")
    for grade in GRADES + ["all"]:
        print(f"  {grade:8} {rates[grade]:5.0%}")
    tokens_in = sum(r["tokens_in"] for r in rows) + USAGE["input"]
    tokens_out = sum(r["tokens_out"] for r in rows) + USAGE["output"]
    cost = tokens_in * 0.15 / 1e6 + tokens_out * 0.60 / 1e6  # gpt-4o-mini, dollars per token
    print(f"agent + judges: {tokens_in:,} input + {tokens_out:,} output tokens · ${cost:.3f}")
