"""Session 3.3, step 6: parallel calls on vs one at a time, the same message many times.

A code check on the outcome (Daniel's waiting list) decides if a run is right:
- Porto (NT-7012) is 10 days away, so the rule says no refund: a Porto refund on the list is wrong.
- Barcelona (NT-7013) may be prepared (1430) or the agent may ask Maria first: both are fine.
"""
import io
import re
import sys
from contextlib import redirect_stdout

from agent import run_agent
from nova_tools import MARIA, WAITING_LIST

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def one_run(parallel):
    WAITING_LIST.clear()  # every run starts with an empty waiting list
    out = io.StringIO()
    with redirect_stdout(out):  # keep the screen short: only the results below
        run_agent(MARIA, parallel=parallel)
    final = re.search(r"Model call (\d+): final answer \((\d+) tokens", out.getvalue())
    calls, tokens = (int(final.group(1)), int(final.group(2))) if final else (0, 0)
    amounts = {r["booking_id"]: r["amount"] for r in WAITING_LIST}
    wrong = "NT-7012" in amounts or amounts.get("NT-7013", 1430) != 1430
    return wrong, calls, tokens, amounts


for parallel in (True, False):
    name = "parallel calls on" if parallel else "one at a time"
    results = [one_run(parallel) for _ in range(RUNS)]
    for i, (wrong, calls, tokens, amounts) in enumerate(results, 1):
        print(f"{name:18} run {i:2}: {'WRONG' if wrong else 'right'} | {calls} model calls | {tokens} tokens | list: {amounts}")
    right = sum(not r[0] for r in results)
    avg_calls = sum(r[1] for r in results) / RUNS
    avg_tokens = sum(r[2] for r in results) / RUNS
    print(f"{name:18} -> right {right} of {RUNS} | {avg_calls:.1f} model calls | {avg_tokens:.0f} tokens on average\n")
