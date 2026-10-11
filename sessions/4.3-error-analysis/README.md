# 4.3 · Error analysis

**Story:** Daniel wants to know what goes wrong with the support agent, and how often.
We send one day of customer messages (40) to the support agent v1, read every trace by hand,
write a short note for each one (open coding), group the notes into failure categories (axial coding),
count them, and stop reading when new traces add no new category (saturation).
For each failed trace we write down the **first** step that went wrong.

## Files

| File | What it is |
|---|---|
| `agent.py`, `tools.py`, `trace_log.py` | the support agent v1, copied unchanged from `labs/01-support-agent/` |
| `data/` | the refund rules and the policy from Lab 1, and more bookings (Olivia, Ben, Maria, Lina, Peter, Hana, Adam) |
| `messages.jsonl` | the 40 customer messages of one day |
| `collect_traces.py` | sends all 40 messages to the agent, in one process, like one day |
| `traces/traces.jsonl` | the real traces of that day (same format as session 3.7 and Lab 1) |
| `traces/runs.jsonl` | which run_id belongs to which message |
| `show_trace.py` | prints one trace in short rows, so a person can read it |
| `labels.jsonl` | one line per trace: the note, pass or fail, the category, the first failure |
| `count_labels.py` | counts the categories and shows where each one first appeared |
| `failure_taxonomy.md` | the result: five failure categories with real examples |

## Run it

From the repository root:

    uv run python sessions/4.3-error-analysis/collect_traces.py    # about 61,000 input tokens, about one cent
    uv run python sessions/4.3-error-analysis/show_trace.py 8
    uv run python sessions/4.3-error-analysis/count_labels.py

`collect_traces.py` adds new runs to `traces/traces.jsonl` and writes a new `traces/runs.jsonl`.
Your runs will differ from ours: a model does not answer the same way every time.
`labels.jsonl` belongs to the traces in this folder. Sessions 4.4 to 4.7 and Lab 2 build on it.
