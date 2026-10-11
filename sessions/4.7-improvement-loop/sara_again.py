"""Sara's refund already waits on Daniel's list. Then she writes again.

    uv run python sessions/4.7-improvement-loop/sara_again.py
    uv run python sessions/4.7-improvement-loop/sara_again.py --prompt v3 --tools v2
"""
import argparse

import tools
from agent import run

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default="v1")
parser.add_argument("--tools", default="v1", choices=["v1", "v2"])
options = parser.parse_args()

tools.WAITING_LIST.append({"kind": "refund", "booking_id": "NT-4821", "amount": 640.0,
                           "reason": "airline_cancelled", "status": tools.WAITING})
message = "Sara again, NT-4821. Did my refund go through yet?"  # case c09
names = tools.V1_TOOLS if options.tools == "v1" else tools.V2_TOOLS
answer, trace = run(message, "gpt-4o-mini", options.prompt, names)

print("Customer:", message)
print("Tools called:", [e["name"] for e in trace.events() if e["type"] == "tool_call"])
print("Agent:", answer)
print("Daniel's waiting list:")
for item in tools.WAITING_LIST:
    print(f"  {item['booking_id']}  {item['amount']}  {item['status']}")
