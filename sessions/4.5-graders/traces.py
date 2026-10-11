"""Small helpers to read the cases and the traces (the JSONL format from session 3.7)."""
import json
from pathlib import Path

HERE = Path(__file__).parent


def load_cases():
    lines = (HERE / "cases.jsonl").read_text().splitlines()
    return {case["message"]: case for case in map(json.loads, lines)}


def load_runs(file=HERE / "traces" / "baseline.jsonl"):
    """All events of the file, grouped by run_id, in order."""
    runs = {}
    for line in Path(file).read_text().splitlines():
        event = json.loads(line)
        runs.setdefault(event["run_id"], []).append(event)
    return runs


def customer_message(events):
    return next(e["args"]["customer"] for e in events if e["type"] == "model_call" and e["args"])


def final_reply(events):
    return next((e["result"] for e in events if e["type"] == "final"), "")
