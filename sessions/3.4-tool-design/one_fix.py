"""Session 3.4: one customer message, five runs, with the tools of one step.

Run:  uv run python sessions/3.4-tool-design/one_fix.py v1 sara_flight
      uv run python sessions/3.4-tool-design/one_fix.py step1 sara_flight
"""
import json
import sys
import tools_steps
import tools_v1
from agent import run_agent
from nova import WAITING_LIST

STEPS = {"v1": (tools_v1.TOOLS, tools_v1.FUNCTIONS),
         "step1": (tools_steps.STEP1_TOOLS, tools_steps.STEP1_FUNCTIONS),
         "step2": (tools_steps.STEP2_TOOLS, tools_steps.STEP2_FUNCTIONS),
         "step3": (tools_steps.STEP3_TOOLS, tools_steps.STEP3_FUNCTIONS)}

MESSAGES = {
    "sara_flight": "hello, is my flight to Lisbon still happening? my booking is nt 4821",
    "john_refund": "This is John, booking NT-5107. I changed my mind about Rome. Please refund me.",
    "sara_refund": "The airline cancelled my flight to Lisbon. Booking NT-4821. Please give me my money back.",
}

step, message = sys.argv[1], sys.argv[2]
runs = int(sys.argv[3]) if len(sys.argv) > 3 else 5
tools, functions = STEPS[step]
for run in range(1, runs + 1):
    WAITING_LIST.clear()
    out = run_agent(MESSAGES[message], tools, functions,
                    run_id=f"{step}-{message}-{run}", trace_file="one_fix.jsonl")
    print(f"run {run}:")
    for call in out["calls"]:
        print(f"  {call['name']}({json.dumps(call['args'])}) -> {json.dumps(call['result'])}")
    print(f"  answer: {out['answer']}")
    print(f"  Daniel's list: {json.dumps(WAITING_LIST)}")
