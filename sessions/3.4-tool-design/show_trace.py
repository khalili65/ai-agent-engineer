"""Session 3.4: print one run of a test, step by step, from its trace file.

Run:  uv run python sessions/3.4-tool-design/show_trace.py test_v1.jsonl "v1-John: price-1"
"""
import json
import sys
from pathlib import Path

trace_file, run_id = sys.argv[1], sys.argv[2]
for line in open(Path(__file__).parent / "traces" / trace_file):
    row = json.loads(line)
    if row["run_id"] != run_id or row["type"] == "model_call":
        continue
    if row["type"] == "tool_call":
        print(f"step {row['step']}  the model calls {row['name']}({json.dumps(row['args'])})")
        print(f"        the tool sends back {json.dumps(row['result'])}")
    else:
        print(f"step {row['step']}  the answer: {row['result']}")
