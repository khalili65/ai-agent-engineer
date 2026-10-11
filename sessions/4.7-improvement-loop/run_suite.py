"""Run one eval suite against one version of the support agent and print a score.

    uv run python sessions/4.7-improvement-loop/run_suite.py capability
    uv run python sessions/4.7-improvement-loop/run_suite.py regression --prompt v2 --trials 3
    uv run python sessions/4.7-improvement-loop/run_suite.py capability --model gpt-6-astra --trials 1

A version = model + prompt + tools. Every case runs --trials times, because the same
message can get a different answer each time. Score = passed runs / all runs.
"""
import argparse
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import tools
from agent import run
from graders import check_case, promise_judge

SUITES = Path(__file__).parent / "suites"
# Dollars per million tokens (input, output), from the OpenAI pricing page.
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-6-luna": (0.10, 0.50),
          "gpt-6.1-sol": (2.00, 10.00), "gpt-6-astra": (10.00, 50.00)}


def load(suite):
    return [json.loads(line) for line in (SUITES / f"{suite}.jsonl").read_text().splitlines()]


def run_suite(suite, model="gpt-4o-mini", prompt="v1", tool_set="v1", trials=1, show=True):
    names = tools.V1_TOOLS if tool_set == "v1" else tools.V2_TOOLS
    passed = total = tokens_in = tokens_out = 0
    for case in load(suite):
        ok, notes = 0, []
        for _ in range(trials):
            before = [dict(item) for item in case.get("waiting_list", [])]
            tools.WAITING_LIST[:] = [dict(item) for item in before]  # the list before this message
            with redirect_stdout(io.StringIO()):
                answer, trace = run(case["message"], model, prompt, names)
            for e in trace.events():
                tokens_in += e["input_tokens"] or 0
                tokens_out += e["output_tokens"] or 0
            problems = check_case(case, answer, trace, before)
            if case["expected"].get("no_promise"):
                verdict, reason, _ = promise_judge(answer)
                if verdict != "PASS":
                    problems.append("promise judge: FAIL")
            if problems:
                notes.append(f"run {trace.run_id}: {'; '.join(problems)}")
            else:
                ok += 1
        passed += ok
        total += trials
        if show:
            mark = "PASS" if ok == trials else "FAIL"
            text = " ".join(case["message"].split())  # one line, even if the message has line breaks
            print(f"{mark} {case['id']}  {ok}/{trials}  {text[:58]}")
            for note in notes[:2]:
                print(f"         {note}")
    price_in, price_out = PRICES.get(model, (0, 0))
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    score = passed / total
    if show:
        print(f"\n{suite} · {model} · prompt {prompt} · tools {tool_set}")
        print(f"score {passed}/{total} = {score:.0%} · agent tokens {tokens_in:,} in + {tokens_out:,} out · ${cost:.4f}")
    return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=["capability", "regression"])
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--prompt", default="v1")
    parser.add_argument("--tools", default="v1", choices=["v1", "v2"])
    parser.add_argument("--trials", type=int, default=3)
    options = parser.parse_args()
    run_suite(options.suite, options.model, options.prompt, options.tools, options.trials)
