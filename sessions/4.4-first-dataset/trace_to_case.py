"""Turn one real trace into a draft test case.

    uv run python sessions/4.4-first-dataset/trace_to_case.py source_traces/day_traces.jsonl 3f884a

It prints what the agent did in that run, and a draft case line.
The trace gives us the customer's message. A person writes "expected": what must be true.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
trace_file, run_id = HERE / sys.argv[1], sys.argv[2]

lines = [json.loads(line) for line in trace_file.read_text().splitlines()]
run = [e for e in lines if e["run_id"] == run_id]

message = run[0]["args"]["customer"]  # the first model_call holds the customer's message
print("Customer:", message)
print("What the agent did:")
for e in run:
    if e["type"] == "tool_call":
        print(f"  {e['name']}({json.dumps(e['args'])})")
    if e["type"] == "final":
        print("  reply:", e["result"])

draft = {"id": "c??", "message": message, "expected": {}, "tags": [], "source": f"trace:{run_id}"}
print("\nDraft case (a person fills in expected and tags):")
print(json.dumps(draft))
