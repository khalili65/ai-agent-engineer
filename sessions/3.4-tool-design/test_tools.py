"""Session 3.4: the same six customer messages, five runs each, with tools version 1 or 2.

Run:  uv run python sessions/3.4-tool-design/test_tools.py v1
      uv run python sessions/3.4-tool-design/test_tools.py v2
"""
import re
import sys
import tools_v1
import tools_v2
from agent import run_agent

VERSION = sys.argv[1] if len(sys.argv) > 1 else "v2"
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
tools = tools_v1 if VERSION == "v1" else tools_v2

# Each test: the message, the tools that fit it (per version), and how we check the result
TESTS = [
    {"name": "John: price", "fact": r"380",
     "message": "Hi, this is John. How much did I pay for my Rome trip? Booking NT-5107.",
     "fits": {"v1": {"get_booking_price", "get_data"}, "v2": {"find_booking"}}},
    {"name": "Sara: flight", "fact": r"\bcancell?ed\b",
     "message": "hello, is my flight to Lisbon still happening? my booking is nt 4821",
     "fits": {"v1": {"get_data"}, "v2": {"find_booking"}}},
    {"name": "Lukas: dates", "fact": r"(12|twelfth).*(16|sixteenth)",
     "message": "This is Lukas. What are the dates of my Paris trip? The booking number is 6190.",
     "fits": {"v1": {"get_booking_dates", "get_data"}, "v2": {"find_booking"}}},
    {"name": "Rules question", "fact": r"14.*50|50.*14",
     "message": "If I change my mind and cancel a trip, do I get my money back?",
     "fits": {"v1": {"rules"}, "v2": {"get_refund_rules"}}},
    {"name": "John: refund", "refund": ("NT-5107", 330),
     "message": "This is John, booking NT-5107. I changed my mind about Rome. Please refund me.",
     "fits": {"v1": {"get_data", "get_booking_price", "get_booking_dates", "rules", "refund"},
              "v2": {"find_booking", "get_refund_rules", "prepare_refund"}}},
    {"name": "Sara: refund", "refund": ("NT-4821", 640),
     "message": "The airline cancelled my flight to Lisbon. Booking NT-4821. "
                "Please give me my money back.",
     "fits": {"v1": {"get_data", "get_booking_price", "rules", "refund"},
              "v2": {"find_booking", "get_refund_rules", "prepare_refund"}}},
]

def is_error(result):
    return isinstance(result, dict) and "error" in result

def refund_ok(call, booking_id, amount):
    """The refund request on Daniel's list must have the right booking and a number amount."""
    args = call["args"]
    got_id = args.get("booking_id", args.get("id"))
    return got_id == booking_id and isinstance(args.get("amount"), (int, float)) \
        and abs(args["amount"] - amount) < 0.01

PROMISE = r"has been (processed|approved|issued|refunded|sent)|is (processed|approved)"

totals = {"promised": 0, "right": 0, "wrong_tool": 0, "arg_errors": 0, "calls": 0, "tokens": 0}
for test in TESTS:
    line = []
    for run in range(1, RUNS + 1):
        tools.WAITING_LIST.clear()
        out = run_agent(test["message"], tools.TOOLS, tools.FUNCTIONS,
                        run_id=f"{VERSION}-{test['name']}-{run}", trace_file=f"test_{VERSION}.jsonl")
        names = [c["name"] for c in out["calls"]]
        wrong = [n for n in names if n not in test["fits"][VERSION]]
        errors = [c for c in out["calls"] if is_error(c["result"])]
        if "refund" in test:
            refunds = [c for c in out["calls"] if c["name"] in ("refund", "prepare_refund")]
            if refunds and not refund_ok(refunds[-1], *test["refund"]):
                errors.append(refunds[-1])  # bad arguments on the refund request
            right = bool(refunds) and refund_ok(refunds[-1], *test["refund"])
        else:
            right = bool(re.search(test["fact"], out["answer"], re.I | re.S))
        totals["right"] += right
        totals["promised"] += bool(re.search(PROMISE, out["answer"], re.I))
        totals["wrong_tool"] += len(wrong)
        totals["arg_errors"] += len(errors)
        totals["calls"] += len(names)
        totals["tokens"] += out["input_tokens"]
        line.append(f"run {run}: {'RIGHT' if right else 'WRONG'} "
                    f"{', '.join(f'{c['name']}({c['args']})' for c in out['calls']) or 'no tool'}")
        if not right:
            line.append(f"        answer: {out['answer'][:160]!r}")
    print(f"== {test['name']} ==")
    print("\n".join("  " + l for l in line))

n = len(TESTS) * RUNS
print(f"\nTools {VERSION}: {totals['right']} of {n} right | "
      f"{totals['wrong_tool']} wrong tool calls | {totals['arg_errors']} argument errors | "
      f"{totals['calls']} tool calls | {totals['tokens']:,} input tokens")
print(f"Answers that say the money is already approved or sent: {totals['promised']} of {n}")
