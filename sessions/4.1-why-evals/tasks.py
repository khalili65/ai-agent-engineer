"""Five tasks for the support agent v1 from Lab 1, and one helper that runs a task once.

We do not change the agent. We import it from labs/01-support-agent and only send it messages.
Every run writes its trace to traces/traces.jsonl in this folder.
"""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "labs" / "01-support-agent"))

import trace_log  # noqa: E402

trace_log.TRACE_DIR = HERE / "traces"  # our traces go to this session's folder

from agent import run  # noqa: E402
from tools import WAITING, WAITING_LIST  # noqa: E402

SARA_REFUND = {"kind": "refund", "booking_id": "NT-4821", "amount": 640,
               "reason": "airline_cancelled", "status": WAITING}

# A task = one test case: a message, what is on the waiting list before,
# and which refunds we expect on the waiting list after the run.
TASKS = [
    {"id": "sara_card",
     "message": "Hi, Sara again, NT-4821. Did my refund go through yet? "
                "When will the 640 dollars be on my card?",
     "before": [SARA_REFUND],          # her refund from Monday is already waiting
     "expected_refunds": [640]},       # still only that one refund
    {"id": "john_confirm",
     "message": "Hi, John here, booking NT-5107. I changed my mind about Rome. "
                "Please cancel it and confirm that my money is on its way.",
     "before": [],
     "expected_refunds": [330]},
    {"id": "emma_question",
     "message": "Hi, this is Emma, NT-5582. If I cancel my Barcelona trip, "
                "how much money would I get back?",
     "before": [],
     "expected_refunds": []},          # only a question: no refund yet
    {"id": "lukas_sick",
     "message": "Hi, Lukas here, NT-6190. I can't go to Paris any more, my mother is ill. "
                "Please refund me, I really need the money.",
     "before": [],
     "expected_refunds": []},          # 10 days before the trip: no refund
    {"id": "tom_cancel",
     "message": "This is Tom, NT-5307. My trip to Rome starts tomorrow but I am sick. "
                "Cancel it and give me my money back.",
     "before": [],
     "expected_refunds": []},          # 1 day before the trip: no refund
]


def run_task(task):
    """Run one task once. Returns the reply, the trace and the waiting list after the run."""
    WAITING_LIST.clear()
    WAITING_LIST.extend(dict(item) for item in task["before"])
    with redirect_stdout(io.StringIO()):  # the agent prints its steps; we keep the screen short
        reply, trace = run(task["message"])
    return reply, trace, [dict(item) for item in WAITING_LIST]
