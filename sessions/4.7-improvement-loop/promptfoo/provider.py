"""A Promptfoo provider: Promptfoo sends one customer message, our support agent answers it."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # the session folder: agent.py, tools.py
import tools  # noqa: E402
from agent import run  # noqa: E402


def call_api(prompt, options, context):
    config = options.get("config", {})
    # The refund that already waits for a person, before the message arrives.
    before = json.loads(context["vars"].get("waiting", "[]"))
    tools.WAITING_LIST[:] = before
    names = tools.V2_TOOLS if config.get("tools") == "v2" else tools.V1_TOOLS
    answer, trace = run(prompt, "gpt-4o-mini", config.get("prompt", "v1"), names)
    new_refunds = [item for item in tools.WAITING_LIST[len(before):] if item["kind"] == "refund"]
    return {"output": json.dumps({"reply": answer, "new_refunds": len(new_refunds)})}
