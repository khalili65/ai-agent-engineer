"""Session 3.7: run customer messages through the agent, with a trace for each run.

    uv run python sessions/3.7-read-a-trace/run_customers.py              # Monday morning: sara john lukas
    uv run python sessions/3.7-read-a-trace/run_customers.py sara_seat 3  # one message, three times
    uv run python sessions/3.7-read-a-trace/run_customers.py sara sara_again
"""
import sys
from support_agent import run_agent
from trace_log import Trace
from nova_data import WAITING_FOR_APPROVAL

MESSAGES = {
    "sara": "Hi, this is Sara. The airline cancelled my flight to Lisbon. "
            "My booking is NT-4821. Can I get my money back?",
    "john": "Hello, John here, booking NT-5107. I changed my mind about Rome. "
            "Can I cancel and get a refund?",
    "lukas": "Hi, it's Lukas. I don't want to go to Paris anymore. "
             "Booking NT-6190. How much money do I get back?",
    "sara_seat": "Hi, this is Sara, NT-4821. The airline cancelled my flight. "
                 "Will I also get back the $35 I paid for my seat?",
    "sara_again": "Hi, Sara again. Booking NT-4821. Did my refund go through yet?",
    "john_again": "John here, NT-5107. I changed my mind about Rome. "
                  "Please confirm that my money is on its way.",
}

names = sys.argv[1:] or ["sara", "john", "lukas"]
times = int(names.pop()) if names[-1].isdigit() else 1

for _ in range(times):
    for name in names:
        trace = Trace()
        answer = run_agent(MESSAGES[name], trace)
        print(f"run {trace.run_id} ({name}): {answer}\n")

print("Waiting for a person to approve:")
for refund in WAITING_FOR_APPROVAL:
    print(" ", refund)
