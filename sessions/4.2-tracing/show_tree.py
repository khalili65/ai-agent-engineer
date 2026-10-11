"""Print one trace from traces/spans.jsonl as a tree, with a small timeline bar for every span.

    uv run python sessions/4.2-tracing/show_tree.py            # the last trace in the file
    uv run python sessions/4.2-tracing/show_tree.py 3f9a1c     # the trace whose ID starts with 3f9a1c
"""
import json
import sys
from datetime import datetime

from otel_setup import SPANS_FILE

BAR = 30  # characters for the whole run


def seconds(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()


spans = [json.loads(line) for line in SPANS_FILE.read_text().splitlines()]
wanted = sys.argv[1] if len(sys.argv) > 1 else spans[-1]["context"]["trace_id"][2:]
spans = [s for s in spans if s["context"]["trace_id"][2:].startswith(wanted)]

root = next(s for s in spans if s["parent_id"] is None)
t0, total = seconds(root["start_time"]), seconds(root["end_time"]) - seconds(root["start_time"])


def line(span, depth):
    start = seconds(span["start_time"]) - t0
    ms = (seconds(span["end_time"]) - seconds(span["start_time"])) * 1000
    a = span["attributes"]
    left = round(start / total * BAR)
    bar = " " * left + "#" * max(1, round(ms / 1000 / total * BAR))
    info = ""
    if "gen_ai.usage.input_tokens" in a:
        info = f"in {a['gen_ai.usage.input_tokens']} · out {a['gen_ai.usage.output_tokens']}"
    if "gen_ai.tool.call.arguments" in a:
        info = a["gen_ai.tool.call.arguments"]
    name = "   " * depth + span["name"]
    print(f"{name:<34} {ms:>6.0f} ms  |{bar:<{BAR}}|  {info}")


print(f"trace {root['context']['trace_id'][2:8]}  ·  {len(spans)} spans")
line(root, 0)
children = sorted((s for s in spans if s["parent_id"] == root["context"]["span_id"]),
                  key=lambda s: s["start_time"])
for child in children:
    line(child, 1)
