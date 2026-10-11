"""Measure the promise judge against Daniel's labels.

    uv run python sessions/4.6-trust-your-judge/measure.py v1 dev
    uv run python sessions/4.6-trust-your-judge/measure.py v2 dev
    uv run python sessions/4.6-trust-your-judge/measure.py v2 test    # only once, at the very end

A failure (FAIL) is what we want the judge to find, so we call it a positive.
TPR, the true positive rate: of the replies Daniel marked FAIL, how many the judge also marked FAIL.
TNR, the true negative rate: of the replies Daniel marked PASS, how many the judge also marked PASS.
"""
import json
import sys
from pathlib import Path

from promise_judge import promise_judge

version, group = sys.argv[1], sys.argv[2]
rows = [json.loads(line) for line in (Path(__file__).parent / "data" / f"{group}.jsonl").read_text().splitlines()]

caught = missed = passed = false_alarms = 0
tokens_in = tokens_out = 0
for row in rows:
    verdict, reason, usage = promise_judge(row["message"], row["reply"], version)
    tokens_in, tokens_out = tokens_in + usage.prompt_tokens, tokens_out + usage.completion_tokens
    if row["label"] == "FAIL":
        if verdict == "FAIL":
            caught += 1
        else:
            missed += 1
    else:
        if verdict == "PASS":
            passed += 1
        else:
            false_alarms += 1
    if verdict != row["label"]:  # show every disagreement, so we can read it
        print(f"{row['id']}  Daniel {row['label']}  judge {verdict}")
        print(f"     reply: {row['reply']}")
        print(f"     judge: {reason}")

fails, passes = caught + missed, passed + false_alarms
print(f"\nJudge {version} on {group}: {len(rows)} replies, {fails} FAIL and {passes} PASS by Daniel")
print(f"TPR {caught}/{fails} = {caught / fails:.0%}   failures the judge caught")
print(f"TNR {passed}/{passes} = {passed / passes:.0%}   good replies the judge passed")
print(f"Agreement {caught + passed}/{len(rows)} = {(caught + passed) / len(rows):.0%}")
cost = tokens_in * 0.15 / 1e6 + tokens_out * 0.60 / 1e6  # gpt-4o-mini prices per million tokens
print(f"Tokens {tokens_in} in, {tokens_out} out, about ${cost:.4f}")
