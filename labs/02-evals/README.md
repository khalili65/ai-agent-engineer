# Lab 2 · Catch your agent's mistakes: traces, judges and a CI gate

**Story:** the support agent v1 from Lab 1 answers Nova Travel's customers. Daniel wants to know how good it
really is, and he wants to know it again after every change. In this lab we read its real traces, name its
failures, build a 30-case dataset, write two LLM judges and check them against human labels, fix the most common
failure, prove the fix with numbers, and add an eval gate that can run in GitHub Actions.

## Files (in the order we write them)

| File | Step | What it is |
|---|---|---|
| `agent/` | 1 | a copy of the Lab 1 agent (`agent.py`, `tools.py`, `trace_log.py`, `data/`) with three more bookings (Mia, Omar, Leo) |
| `inbox.jsonl` | 1 | 36 realistic customer messages from one week |
| `collect.py` | 1 | runs the agent on every message and saves the traces in `traces/traces.jsonl` |
| `read_traces.py` | 2 | prints every run in a short form, so a person can read it |
| `notes.csv` | 2 | one note per run (open coding), a category (axial coding) and the first failure |
| `count.py` | 2 | counts the categories |
| `taxonomy.md` | 2 | the failure taxonomy: three categories, counts, examples, how we check each one |
| `synthetic.py` | 3 | writes candidate messages from chosen dimensions; a person keeps only the good ones |
| `cases.jsonl` | 3 | 30 cases: 26 from real traces, 4 careful synthetic ones |
| `checks.py` | 4 | code checks: the right tool, the right refund, the right fee, nothing final without a person |
| `judges.py` | 4 | `promise_judge` and `facts_judge` (gpt-4o-mini, a short reason, then PASS or FAIL) |
| `labels.jsonl` | 4 | 104 replies labelled PASS or FAIL by a person, for both judges |
| `align.py` | 4 | measures a judge against the labels (TPR and TNR) on the dev half or the test half |
| `run_evals.py` | 5 | runs every case 3 times and grades every run with the code checks and both judges |
| `compare.py` | 5 | compares two eval runs, grade by grade and case by case (changes of 2+ runs) |
| `review.py` | 5 | counts a person's review of every `facts_judge` FAIL (`results/<name>_facts_review.csv`) |
| `gate.py` | 6 | the eval gate: exit code 1 when code checks < 80% or `promise_judge` < 90% (`facts_judge` is only a note) |
| `ci/eval-gate.yml` | 6 | the GitHub Actions workflow that runs the cases and the gate |
| `results/` | 5–6 | the committed results with their traces: `v1` (before), `v2`, `v3`, `v4` (the three steps of the fix), `ci` (the workflow commands, 1 trial) |
| `traces/` | 1–4 | this week's traces, plus the Lab 1 and session 3.7 traces used for the labels |

## Run it

From the repository root:

    uv run python labs/02-evals/collect.py                 # 36 messages, about 62,000 tokens
    uv run python labs/02-evals/read_traces.py             # read every run
    uv run python labs/02-evals/count.py
    uv run python labs/02-evals/align.py promise dev       # or: facts dev, promise test, facts test
    uv run python labs/02-evals/run_evals.py --name mine   # 30 cases x 3 trials = 90 runs, about 5 cents
    uv run python labs/02-evals/compare.py v1 mine
    uv run python labs/02-evals/review.py v4
    uv run python labs/02-evals/gate.py mine

Everything uses `gpt-4o-mini` through the `.env` file in the repository root. Building the whole lab, with every
run shown in the video, cost about 30 cents. One trial of the 30 cases took about 2 minutes.

## The fix

The most common failure (8 of 36 runs) was a **refund nobody asked for**: "Did my refund go through yet?" made the
agent prepare a second refund. Fix order: prompt first. The fix took three measured steps in `agent/agent.py`:

| Version | Change | code | promise | facts_judge | facts, checked by a person |
|---|---|---|---|---|---|
| v1 | Lab 1 agent | 71% | 89% | 63% | 76% |
| v2 | prepare a refund only when the customer asks for one | 88% | 84% | 48% | – |
| v3 | + never guess an earlier refund's status; a person will check and reply | 88% | 78% | 46% | – |
| v4 | + "Do not add soon, shortly or any other time." | 87% | 97% | 44% | 90% |

`facts_judge` fell because it marks honest replies such as "a person on our team will check it and reply" as
"not shown" (its test TNR was 81%). A person read all its FAILs: 22 real errors in v1, 9 in v4.
Still open: case c06 ("if I cancel today, how much do I get back?") now prepares a refund, plus c05 (the seat),
c08 (a friend, not the customer) and c13 (refund time without reading the policy). The next step in the fix
order is a tool that can read the waiting list.

## The eval gate in GitHub Actions

`ci/eval-gate.yml` is a ready workflow. It is **not active** in this repository. To switch it on in your own
repository:

1. Move it to `.github/workflows/eval-gate.yml` (GitHub only runs workflows from that folder) and fix the paths
   if your lab folder is somewhere else.
2. Add your key as a repository secret named `OPENAI_API_KEY`: Settings → Secrets and variables → Actions →
   New repository secret.
3. Open a pull request that changes `labs/02-evals/`. The workflow runs the cases (1 trial each: on my computer
   about 2 minutes and 1.5 cents) and the gate. A red check means the change made the agent worse.
