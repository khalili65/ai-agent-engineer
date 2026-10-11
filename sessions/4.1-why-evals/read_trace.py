"""Print the transcript of one trial: every line of its trace, short and in order.

    uv run python sessions/4.1-why-evals/read_trace.py 739145
"""
import json
import sys

from tasks import HERE

run_id = sys.argv[1]
lines = [json.loads(line) for line in (HERE / "traces" / "traces.jsonl").read_text().splitlines()]
for line in lines:
    if line["run_id"] != run_id:
        continue
    if line["type"] == "model_call":
        what = f"{line['name']} -> {line['result']}"
    elif line["type"] == "tool_call":
        what = f"{line['name']} {json.dumps(line['args'])}"
    elif line["type"] == "final":
        what = line["result"]
    else:  # tool_result or error
        what = f"{line['name']} -> {json.dumps(line['result'])[:90]}"
    print(f"{line['step']:>2} {line['type']:<11} {what}")
