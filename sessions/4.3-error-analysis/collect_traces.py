"""One day at Nova Travel: send 40 customer messages to the support agent v1.

    uv run python sessions/4.3-error-analysis/collect_traces.py

All messages run in one process, in order, like one working day. So the waiting list
grows during the day, and a second refund for the same booking stays visible.
Every run writes its trace lines to traces/traces.jsonl.
"""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from agent import run
from tools import WAITING_LIST

HERE = Path(__file__).parent
messages = [json.loads(line) for line in (HERE / "messages.jsonl").read_text().splitlines()]

runs = []
for item in messages:
    with redirect_stdout(io.StringIO()):  # hide the step lines of agent.py
        answer, trace = run(item["message"])
    runs.append({"n": item["n"], "run_id": trace.run_id})
    print(f"{item['n']:>2}  {trace.run_id}  {item['message'][:60]}")

# Which run is which message: we read the traces in this order.
with open(HERE / "traces" / "runs.jsonl", "w") as f:
    for r in runs:
        f.write(json.dumps(r) + "\n")

print(f"\n{len(runs)} runs. Waiting list at the end of the day:")
for entry in WAITING_LIST:
    print(" ", entry)
