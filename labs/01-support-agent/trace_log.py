"""A tiny trace logger: one JSON line for every event of a run (the same format as session 3.7).

Every line has nine fields: run_id, step, type, name, args, result, input_tokens, output_tokens, ms.
type is model_call, tool_call, tool_result, final or error. Fields that do not apply are null.
"""
import json
import uuid
from pathlib import Path

TRACE_DIR = Path(__file__).parent / "traces"


class TraceLog:
    def __init__(self, file="traces.jsonl"):
        self.run_id = uuid.uuid4().hex[:6]  # one id for one customer message
        self.step = 0
        TRACE_DIR.mkdir(exist_ok=True)
        self.path = TRACE_DIR / file

    def log(self, type, name=None, args=None, result=None,
            input_tokens=None, output_tokens=None, ms=None):
        self.step += 1
        event = {"run_id": self.run_id, "step": self.step, "type": type,
                 "name": name, "args": args, "result": result,
                 "input_tokens": input_tokens, "output_tokens": output_tokens, "ms": ms}
        with open(self.path, "a") as f:  # "a" means append: add a line at the end
            f.write(json.dumps(event) + "\n")

    def events(self):
        """All lines of this run, read back from the file."""
        lines = [json.loads(line) for line in self.path.read_text().splitlines()]
        return [e for e in lines if e["run_id"] == self.run_id]
