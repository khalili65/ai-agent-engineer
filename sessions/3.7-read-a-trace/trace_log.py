"""Session 3.7: a tiny trace logger. It writes one JSON line for every event."""
import json
import uuid
from pathlib import Path

TRACE_DIR = Path(__file__).parent / "traces"


class Trace:
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
