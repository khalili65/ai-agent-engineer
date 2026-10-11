# Session 3.7: Read a trace by hand

A customer tells Daniel that the support agent said something strange, and nobody can see what happened inside the agent.
So we add a tiny trace logger: the agent writes one JSON line for every event of a run. Then we read the trace file by hand
and learn to tell three kinds of failure apart.

| File | What it does |
|---|---|
| `nova_data.py` | The bookings (Sara, John, Lukas), the refund rules, and the three tools: `find_booking`, `get_refund_rules`, `prepare_refund` (it only adds the refund to a list for a person; it never sends money). |
| `trace_log.py` | The trace logger: `Trace().log(type, name, args, result, input_tokens, output_tokens, ms)` appends one JSON line to `traces/traces.jsonl`. |
| `support_agent.py` | The agent loop with a `trace.log(...)` call after every model call, tool call, tool result and final answer (and on errors). |
| `run_customers.py` | Sends customer messages to the agent, one run (and one `run_id`) per message. |

```bash
uv run python sessions/3.7-read-a-trace/run_customers.py                  # sara john lukas
uv run python sessions/3.7-read-a-trace/run_customers.py sara_seat 3      # one message, three times
uv run python sessions/3.7-read-a-trace/run_customers.py sara sara_again  # Sara asks twice
uv run python sessions/3.7-read-a-trace/run_customers.py john_again 5

head -n 10 sessions/3.7-read-a-trace/traces/traces.jsonl   # the first run, line by line
grep 1f46c5 sessions/3.7-read-a-trace/traces/traces.jsonl  # every line of one run
```

## The trace format (one JSON object per line)

| Field | Meaning |
|---|---|
| `run_id` | One id for one customer message (all lines of one run share it). |
| `step` | 1, 2, 3 … the order of the events inside the run. |
| `type` | `model_call`, `tool_call`, `tool_result`, `final` or `error`. |
| `name` | The model for a `model_call`, the tool for `tool_call` / `tool_result` / `error`. |
| `args` | The tool's arguments; for the first `model_call`, the customer's message. |
| `result` | The tool's result; for a `model_call`, the finish reason (`tool_calls` or `stop`); for `final`, the reply. |
| `input_tokens`, `output_tokens` | Tokens of a `model_call`. |
| `ms` | How long the model call or the tool took, in milliseconds. |

Fields that do not apply to an event are `null`. Lab 1 and Section 4 use exactly this format.

## Three kinds of failure (read in this order)

1. **Wrong tool**: look at `name` in the `tool_call` lines. Example: Sara asks "Did my refund go through yet?" and the agent calls `prepare_refund` again, so Daniel's list has her refund twice.
2. **Bad arguments**: the right tool, but look at `args`. Example: Sara asks about a $35 seat, and the agent calls `prepare_refund` with `"amount": 35` instead of the full $640.
3. **Bad answer**: every tool line is right, but compare the `final` reply with the tool results. Example: `prepare_refund` says "waiting for a person to approve", and the reply promises "It will be processed shortly."

`traces/traces.jsonl` holds the real traces from the video. Your own runs add new lines at the end, and your replies will differ.
