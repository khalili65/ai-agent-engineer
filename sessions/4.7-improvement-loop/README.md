# Session 4.7: The improvement loop and CI gate

Sara's refund already waits on Daniel's list. She writes again, "Did my refund go through yet?", and the
support agent v1 from Lab 1 prepares a **second** refund. We fix it the careful way: measure, change one
thing, measure again, and read the failures. Then a small gate stops any change that breaks old cases.

| File | What it is |
|---|---|
| `agent.py` | The support agent v1 (Lab 1), copied. The model, the prompt file and the tool list are settings now. gpt-6 models use the Responses API (they refuse function tools on Chat Completions). |
| `tools.py` | Lab 1's tools, plus the new `get_refund_status(booking_id)`. `V1_TOOLS` = Lab 1's five tools, `V2_TOOLS` = plus `get_refund_status`. |
| `prompts/v1.txt` | Lab 1's instructions, unchanged. |
| `prompts/v2.txt` | v1 + two lines: do not prepare a new refund for a refund the customer already asked for; say it waits for a person. |
| `prompts/v3.txt` | v2 + one line: when the customer gives a booking number, always call `find_booking` first. |
| `suites/capability.jsonl` | 6 status questions the agent did not pass yet (a goal). |
| `suites/regression.jsonl` | Cases the agent passes and must keep passing: 10 cases, then 16 after the six status cases "graduated". |
| `suites/next_goals.jsonl` | 5 cases with a promise check that v1 does not pass every time yet (for a later round). |
| `suites/promise_labels.jsonl` | 24 real replies labeled PASS/FAIL by hand, to check the promise judge. |
| `graders.py` | Code checks for the keys of the case file + the binary `promise_judge` (gpt-4o-mini). |
| `check_judge.py` | Compares the judge with the hand labels. |
| `run_suite.py` | Runs one suite on one version (model + prompt + tools), every case `--trials` times, and prints the score. |
| `sara_again.py` | Sara's refund waits; she asks again. Prints the reply and Daniel's waiting list. |
| `ci_gate.py` | Runs the regression suite (2 trials) and exits with code 1 if the score is below 95 %. |
| `ci/eval-gate.yml` | The GitHub Actions workflow for the gate (not active, see below). |
| `promptfoo/` | The same idea with Promptfoo: `promptfooconfig.yaml` and `provider.py`. |

## Case format

The cases use the shared format of session 4.4 (`id`, `message`, `expected`, `tags`, `source`; `expected` keys
`tool`, `amount`, `refund`, `fee`, `no_promise`). Cases c01–c46 are copied from `sessions/4.4-first-dataset/cases.jsonl`;
c47–c53 are new. One addition: status cases have a `waiting_list` field, the refunds that already wait before
the message arrives. The checks only look at what **this run** adds to the list, so `refund: false` means
"this run prepares no refund".

## Run it

From the repository root:

    uv run python sessions/4.7-improvement-loop/sara_again.py
    uv run python sessions/4.7-improvement-loop/check_judge.py
    uv run python sessions/4.7-improvement-loop/run_suite.py capability                          # v1
    uv run python sessions/4.7-improvement-loop/run_suite.py capability --prompt v2
    uv run python sessions/4.7-improvement-loop/run_suite.py capability --prompt v2 --tools v2
    uv run python sessions/4.7-improvement-loop/run_suite.py regression --prompt v3 --tools v2
    uv run python sessions/4.7-improvement-loop/run_suite.py capability --model gpt-6-astra --trials 1
    uv run python sessions/4.7-improvement-loop/ci_gate.py; echo "exit code $?"
    uv run python sessions/4.7-improvement-loop/ci_gate.py --prompt v2; echo "exit code $?"

    uv run npx promptfoo@0.124.1 eval -c sessions/4.7-improvement-loop/promptfoo/promptfooconfig.yaml -j 1
    npx promptfoo@0.124.1 view

Costs with gpt-4o-mini: one suite run is well under one cent. A run on gpt-6-astra costs about 2 cents per
message (the capability suite with one trial: about 15 cents). Promptfoo needs Node.js; it runs locally, no account.
`-j 1` matters: the waiting list is one Python list, so cases must run one after another.

Your scores will differ a little from ours: the same message can get a different answer each time.

## Turn on the CI gate on GitHub

`ci/eval-gate.yml` is not active here. To use it in your own repository:

1. Copy it to `.github/workflows/eval-gate.yml`.
2. Add the repository secret `OPENAI_API_KEY` (Settings → Secrets and variables → Actions → New repository secret).

It runs on every pull request that changes this folder. One run costs about one cent.
