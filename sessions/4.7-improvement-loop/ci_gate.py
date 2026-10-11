"""The CI gate: run the regression suite and fail when the score drops below the line.

    uv run python sessions/4.7-improvement-loop/ci_gate.py
    uv run python sessions/4.7-improvement-loop/ci_gate.py --prompt v2     # an older prompt

Exit code 0 = the gate passes, exit code 1 = the gate fails. CI tools stop on exit code 1.
"""
import argparse
import sys

from run_suite import run_suite

MIN_SCORE = 0.95  # at most one failed run out of 32 (16 cases, 2 trials each)

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="gpt-4o-mini")
parser.add_argument("--prompt", default="v3")   # the version we use today
parser.add_argument("--tools", default="v2")
parser.add_argument("--trials", type=int, default=2)
options = parser.parse_args()

score = run_suite("regression", options.model, options.prompt, options.tools, options.trials)
if score < MIN_SCORE:
    print(f"GATE FAILED: regression score {score:.0%} is below {MIN_SCORE:.0%}")
    sys.exit(1)
print(f"GATE PASSED: regression score {score:.0%} (minimum {MIN_SCORE:.0%})")
