"""Step 4c: measure each judge against the human labels.

    uv run python labs/02-evals/align.py promise dev     # look at every disagreement, improve the prompt
    uv run python labs/02-evals/align.py promise test    # only once, at the end: the honest number

FAIL is what we hunt, so a FAIL is a "positive".
TPR (true positive rate): of the replies a person marked FAIL, how many the judge also marked FAIL.
TNR (true negative rate): of the replies a person marked PASS, how many the judge also marked PASS.
"""
import json
import sys
from pathlib import Path

from judges import USAGE, facts_judge, promise_judge
from read_traces import load_runs

HERE = Path(__file__).parent
TRACE_FILES = ["traces.jsonl", "lab1_traces.jsonl", "s3_7_traces.jsonl"]


def split(labels):
    """Half for dev, half for test, with the same mix of PASS and FAIL in each half."""
    labels = sorted(labels, key=lambda x: (x["promise"], x["facts"], x["run_id"]))
    return {"dev": labels[0::2], "test": labels[1::2]}


if __name__ == "__main__":
    judge, part = sys.argv[1], sys.argv[2]  # promise or facts; dev or test
    runs = {}
    for name in TRACE_FILES:
        runs.update(load_runs(HERE / "traces" / name))
    labels = [json.loads(line) for line in (HERE / "labels.jsonl").read_text().splitlines()]
    rows = split(labels)[part]

    caught = fails = passed = passes = 0
    for row in rows:
        events = runs[row["run_id"]]
        message = next(e["args"]["customer"] for e in events if e["type"] == "model_call")
        reply = next(e["result"] for e in events if e["type"] == "final")
        if judge == "promise":
            verdict, reason = promise_judge(message, reply)
        else:
            verdict, reason = facts_judge(message, events, reply)
        human = row[judge]
        if human == "FAIL":
            fails += 1
            caught += verdict == "FAIL"
        else:
            passes += 1
            passed += verdict == "PASS"
        if verdict != human:  # show every disagreement, so we can read it
            print(f"{row['run_id']}  human {human}  judge {verdict}")
            print(f"    reply: {reply}")
            print(f"    judge: {reason}")
    print(f"\n{judge}_judge on {part}: {len(rows)} replies, {fails} FAIL and {passes} PASS by a person")
    print(f"TPR {caught}/{fails} = {caught / fails:.0%}   failures the judge caught")
    print(f"TNR {passed}/{passes} = {passed / passes:.0%}   good replies the judge passed")
    cost = USAGE["input"] * 0.15 / 1e6 + USAGE["output"] * 0.60 / 1e6  # gpt-4o-mini, dollars per token
    print(f"{USAGE['input']:,} input + {USAGE['output']:,} output tokens · ${cost:.4f}")
