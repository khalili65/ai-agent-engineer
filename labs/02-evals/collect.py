"""Step 1: run the support agent v1 on a week of real-looking customer messages and keep every trace.

    uv run python labs/02-evals/collect.py

The agent in agent/ is a copy of Lab 1 (same code, three more bookings in data/).
All traces go to traces/traces.jsonl, one JSON line per event (the format of session 3.7).
"""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "agent"))  # so we can import the agent's files

import trace_log  # noqa: E402
from agent import run  # noqa: E402
from tools import WAITING_LIST  # noqa: E402

trace_log.TRACE_DIR = HERE / "traces"  # our traces live in this lab, not in the agent folder
OUT = HERE / "traces" / "traces.jsonl"

if __name__ == "__main__":
    OUT.unlink(missing_ok=True)  # start with an empty file
    inbox = [json.loads(line) for line in (HERE / "inbox.jsonl").read_text().splitlines()]
    tokens = 0
    for item in inbox:
        WAITING_LIST.clear()
        with redirect_stdout(io.StringIO()):  # keep the screen short
            answer, trace = run(item["message"])
        lines = trace.events()
        tokens += sum((e["input_tokens"] or 0) + (e["output_tokens"] or 0) for e in lines)
        tools = [e["name"] for e in lines if e["type"] == "tool_call"]
        print(f"{item['id']}  run {trace.run_id}  tools: {', '.join(tools) or '-'}")
    runs = len(inbox)
    print(f"\n{runs} runs · {len(OUT.read_text().splitlines())} trace lines · {tokens:,} tokens · {OUT.relative_to(HERE)}")
