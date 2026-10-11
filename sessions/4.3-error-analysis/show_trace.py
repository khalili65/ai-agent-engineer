"""Print one trace so a person can read it: one short row per line of the trace.

    uv run python sessions/4.3-error-analysis/show_trace.py 8      # the 8th message of the day
    uv run python sessions/4.3-error-analysis/show_trace.py 1f46c5 # or a run_id
"""
import json
import sys
from pathlib import Path

TRACES = Path(__file__).parent / "traces"
lines = [json.loads(line) for line in (TRACES / "traces.jsonl").read_text().splitlines()]
runs = [json.loads(line) for line in (TRACES / "runs.jsonl").read_text().splitlines()]

wanted = sys.argv[1]
if wanted.isdigit():  # a number means: the n-th message of the day
    wanted = runs[int(wanted) - 1]["run_id"]


def short(value, width=90):
    text = value if isinstance(value, str) else json.dumps(value)
    text = text.replace("\n", " ")
    return text if len(text) <= width else text[:width - 3] + "..."


for e in [e for e in lines if e["run_id"] == wanted]:
    if e["type"] == "model_call":
        what = (f"-> {e['result']}   ({e['input_tokens']} in, {e['output_tokens']} out)"
                + (f"\n      customer: {e['args']['customer']}" if e["args"] else ""))
    elif e["type"] == "tool_call":
        what = f"{e['name']} {short(e['args'])}"
    elif e["type"] == "final":
        what = "\n      " + e["result"]
    else:  # tool_result or error
        what = f"{e['name']} -> {short(e['result'])}"
    print(f"{e['step']:>3}  {e['type']:<11} {what}")
