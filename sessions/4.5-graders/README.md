# Session 4.5: Graders

Session 4.4 built the case file (46 cases) and ran the support agent v1 once on every case.
Who decides which of those runs are good? Three kinds of graders, cheapest first:
code checks, binary LLM judges, and a person.

| Step | File | What it does |
|---|---|---|
| 1 | `code_checks.py` | Three plain functions grade every trace: `check_tool`, `check_amount`, `check_nothing_sent`. They read every tool call of the trace, not only the final reply. No model, no cost. |
| 2 | `run_judges.py` | Runs the two binary judges from `judges.py` on every final reply: `promise_judge` and `facts_judge`. Each answers with a short reason first, then PASS or FAIL alone on the last line. Saves `judged.jsonl`. |
| – | `score_1_to_10.py` | Why we do not use a score from 1 to 10: three real replies, scored five times each, next to the PASS/FAIL judge. |
| – | `word_list_vs_judge.py` | The rough word check from session 4.4 next to `promise_judge`, on two test replies we wrote ourselves. |
| 3 | `review_sample.py` | Builds `review_sheet.csv` for Daniel: every reply a judge failed, plus 5 random replies both judges passed. |

Run from the repository root:

```bash
uv run python sessions/4.5-graders/code_checks.py
uv run python sessions/4.5-graders/run_judges.py
uv run python sessions/4.5-graders/score_1_to_10.py
uv run python sessions/4.5-graders/word_list_vs_judge.py
uv run python sessions/4.5-graders/review_sample.py
```

Files
- `cases.jsonl`: the 46 cases from session 4.4 (`id`, `message`, `expected`, `tags`, `source`).
- `traces/baseline.jsonl`: the 46 real runs of the session 4.4 baseline (one run per case, the trace format from session 3.7). To grade new runs, run `sessions/4.4-first-dataset/run_baseline.py` and copy its `traces/traces.jsonl` here.
- `traces.py`: small helpers that read the cases and the traces.
- `judged.jsonl`: the verdicts and reasons from the video's judge run.
- `review_sheet_daniel.csv`: the review sheet with Daniel's own verdicts filled in (human labels). Session 4.6 uses labels like these to measure the judge.

Notes
- The judges use `gpt-4o-mini` at `temperature=0`. Your verdicts can differ a little from the video.
- A judge makes mistakes. In the video, the promise judge missed one promise, and the facts judge failed three good replies. Session 4.6 measures how often a judge agrees with a person.
- The whole session costs a few cents with `gpt-4o-mini`.
