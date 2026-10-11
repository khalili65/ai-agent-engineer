"""Step 2a: print every run of a trace file in a short form, so a person can read them one by one.

    uv run python labs/02-evals/read_traces.py                # all runs
    uv run python labs/02-evals/read_traces.py 38e205         # one run
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def load_runs(path):
    """Group the trace lines by run_id, in the order the runs happened."""
    runs = {}
    for line in Path(path).read_text().splitlines():
        event = json.loads(line)
        runs.setdefault(event["run_id"], []).append(event)
    return runs


def short(value, width=110):
    text = value if isinstance(value, str) else json.dumps(value)
    return text if len(text) <= width else text[:width - 1] + "…"


def show(run_id, events):
    customer = next(e["args"]["customer"] for e in events if e["type"] == "model_call")
    print(f"=== run {run_id}")
    print(f"customer: {customer}")
    for e in events:
        if e["type"] == "tool_call":
            print(f"  {e['step']:>2} call    {e['name']}({short(e['args'], 80)})")
        elif e["type"] in ("tool_result", "error"):
            print(f"  {e['step']:>2} {e['type'][:6]:7} {short(e['result'])}")
        elif e["type"] == "final":
            print(f"agent: {e['result']}\n")


if __name__ == "__main__":
    runs = load_runs(HERE / "traces" / "traces.jsonl")
    wanted = sys.argv[1:] or list(runs)
    for run_id in wanted:
        show(run_id, runs[run_id])
