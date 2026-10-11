# Session 4.4: Your first dataset

Daniel's team has read a whole day of traces and found real failures. Now they turn those failures into
test cases that they can run again after every change: the first dataset of the support agent.

| File | What it is |
|---|---|
| `cases.jsonl` | **The dataset**: 46 test cases, one JSON object per line (format below). |
| `source_traces/` | Copies of the real traces the cases come from: `day_traces.jsonl` (session 4.3), `lab1_traces.jsonl` (Lab 1), `s3_7_traces.jsonl` (session 3.7). |
| `trace_to_case.py` | Shows what the agent did in one traced run and prints a draft case. A person writes `expected`. |
| `check_cases.py` | Checks every line, works out every amount and fee again from the refund rules, and counts the cases by source and tag. |
| `make_synthetic.py` | Asks the model to write customer messages for mixes of tone × request × edge. The expected result comes from the rules in code, never from the model. |
| `synthetic_candidates.jsonl` | The 24 messages the model wrote. |
| `synthetic_review.jsonl` | A person's decision for every candidate: keep or reject, and why. |
| `add_synthetic.py` | Adds the kept candidates to `cases.jsonl`. |
| `support_agent_v1.py` | Loads the support agent v1 from Lab 1 unchanged; it only adds the new bookings and writes traces here. |
| `run_baseline.py` | Runs v1 once on every case with simple code checks: the first baseline score. |
| `data/bookings.json` | The 13 bookings of session 4.3 (Lab 1's five plus eight more, e.g. Olivia 14 days, Ben 15 days before the trip). |

## The case format (`cases.jsonl`)

One JSON object per line, with five fields:

| Field | Meaning |
|---|---|
| `id` | `"c01"`, `"c02"`, … |
| `message` | The customer's message, exactly as the agent gets it. |
| `expected` | What must be true after the run (only the keys that matter for this case, see below). |
| `tags` | Short labels to count and filter cases, e.g. `["refund", "edge_14_days"]`. Ten cases carry `golden`. |
| `source` | `"trace:<run_id>"` (from a real trace), `"written"` (written by a person) or `"synthetic"` (written by a model, reviewed by a person). |

Keys in `expected`:

| Key | Meaning |
|---|---|
| `tool` | This tool must be called, e.g. `"prepare_refund"`. |
| `amount` | Exactly one refund is on the waiting list, with this amount. |
| `refund` | `false`: no refund may be on the waiting list. |
| `fee` | The change on the waiting list has this fee. |
| `no_promise` | `true`: the reply must not promise an approval or a time that only a person can give. |

Example:

```json
{"id": "c04", "message": "Hi, Olivia here, NT-6624. My Vienna trip is in exactly two weeks, but I can't go any more. Please refund me.", "expected": {"refund": false}, "tags": ["refund", "changed_mind", "edge_14_days", "wrong_amount", "golden"], "source": "trace:0e4cbf"}
```

## Run it

From the repository root:

    uv run python sessions/4.4-first-dataset/trace_to_case.py source_traces/day_traces.jsonl 3f3ec4
    uv run python sessions/4.4-first-dataset/check_cases.py
    uv run python sessions/4.4-first-dataset/make_synthetic.py 24
    uv run python sessions/4.4-first-dataset/run_baseline.py

`make_synthetic.py` overwrites `synthetic_candidates.jsonl` with new messages, and they will differ from ours.
Then read every candidate and write your own decisions in `synthetic_review.jsonl` before you run `add_synthetic.py`
(it stops if `cases.jsonl` already has synthetic cases).

The baseline makes one agent run per case: 46 runs, about 86,000 tokens, under two cents with `gpt-4o-mini`.
Our run: **36 of 46 passed**. Five refunds were prepared that nobody asked for (four of them for questions
about a refund), and six replies promised something (found by a rough word check; session 4.5 builds a real judge).
Your score will differ a little from run to run.
