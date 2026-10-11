# Session 4.1: Why evals

The support agent v1 from Lab 1 passed its 10-case smoke check. Daniel asks: can we trust it with real customers?
First we try a vibe check: send five new messages once and read the replies. They all look good.
Then we run every message five times and look at more than the reply: the waiting list after the run and the trace.
Real failures appear that the quick look missed. On the way we learn five words: task, trial, grader, transcript, outcome.

We do not change the agent. These files import it from `labs/01-support-agent/` and only send it messages.

| File | What it does |
|---|---|
| `tasks.py` | Five tasks (Sara, John, Emma, Lukas, Tom): a message, the waiting list before the run, and the refunds we expect after it. `run_task(task)` runs one task once and writes its trace to `traces/traces.jsonl` in this folder. |
| `vibe_check.py` | Sends each message once and prints only the replies, the way a quick look works. |
| `trials.py` | Runs every task several times (trials). A code grader checks the outcome: exactly the expected refunds on the waiting list. Saves every trial and its reply to `results.jsonl`. |
| `read_trace.py` | Prints the transcript of one trial (one run id), one short line per trace event. |

```bash
uv run python sessions/4.1-why-evals/vibe_check.py
uv run python sessions/4.1-why-evals/trials.py        # 5 trials per task, 25 runs
uv run python sessions/4.1-why-evals/trials.py 3      # 3 trials per task
uv run python sessions/4.1-why-evals/read_trace.py <run_id>
```

The agent uses `gpt-4o-mini` by default (from `.env`). 30 runs (one vibe check and 25 trials) used about
63,000 input and 3,100 output tokens, about one cent.

## The five words

| Word | Meaning | In this session |
|---|---|---|
| task | one test case: an input and what success means | Emma asks how much she would get back; success = no refund on the list yet |
| trial | one run of a task; agents vary, so we run each task several times | 5 trials per task |
| grader | what decides pass or fail: code, a model, or a person | `grade_outcome` in `trials.py` (code); a person reads the replies; model graders come in session 4.5 |
| transcript | the full record of one trial | our JSONL trace (`read_trace.py`) |
| outcome | the final state after the trial, not what the reply says | the waiting list |

The words come from Anthropic's engineering article "Demystifying evals for AI agents".
