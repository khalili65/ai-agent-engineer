# Lab 1 · Build a support agent from scratch

**Story:** Nova Travel gets many customer messages every day: refunds, date changes and questions about bags.
In this lab we build the support agent v1 with plain Python and no framework. It finds bookings, reads the
refund rules and the travel policy, and prepares refunds and changes. It never sends money: every refund
waits on a list until a person approves it (Daniel's rule).

## Files (in the order we write them)

| File | What it is |
|---|---|
| `data/bookings.json` | five example bookings (Sara, John, Tom, Emma, Lukas) |
| `data/rules.md` | the refund rules |
| `data/policy.md` | the travel policy: baggage, changes, cancellations |
| `tools.py` | the tools (plain Python functions), the dispatch table `TOOLS` and the tool descriptions `TOOL_SPECS` |
| `tests/test_tools.py` | quick tests for the tools (no model, no key, no cost) |
| `trace_log.py` | adds one JSON line per event to `traces/traces.jsonl` (same format as session 3.7) |
| `agent.py` | the agent loop, once for OpenAI (Chat Completions) and once for Claude (Messages API) |
| `smoke_check.py` | ten real customer messages with simple code checks |

## Run it

From the repository root:

    uv run pytest labs/01-support-agent
    uv run python labs/01-support-agent/agent.py
    uv run python labs/01-support-agent/agent.py "Hi, Emma here. How many bags can I take on my Barcelona trip?"
    uv run python labs/01-support-agent/smoke_check.py

The agent uses the settings in your `.env` file (see `.env.example`), with `gpt-4o-mini` by default.
One smoke check (ten messages) uses about 17,000 tokens: well under one cent with `gpt-4o-mini`.

### Limits

Every run stops after `MAX_STEPS` model calls (default 6) or when it has used more than `TOKEN_BUDGET`
tokens (default 20,000). Then the customer gets a polite hand-off message. You can try them:

    TOKEN_BUDGET=800 uv run python labs/01-support-agent/agent.py
    MAX_STEPS=2 uv run python labs/01-support-agent/agent.py

### Claude

The same agent runs on the Claude Messages API:

    uv run python labs/01-support-agent/agent.py --provider claude
    uv run python labs/01-support-agent/smoke_check.py --provider claude

This needs an Anthropic key: add `ANTHROPIC_API_KEY=...` to `.env` (optional: `CLAUDE_MODEL=...`, default
`claude-haiku-5-5`). Without a key you get the error
`Could not resolve authentication method. Expected one of api_key, auth_token, or credentials to be set`.

## Traces

Every run adds its lines to `traces/traces.jsonl`, one JSON object per line, in the same format as session 3.7:
`run_id` (6 hex characters), `step` (1, 2, 3 … for every line of a run), `type` (`model_call` | `tool_call` |
`tool_result` | `final` | `error`), `name`, `args`, `result`, `input_tokens`, `output_tokens`, `ms`. Fields that do not
apply are `null`. A `model_call` has the model as `name` and the finish reason (`tool_calls` or `stop`) as `result`;
the first one of a run has `args` `{"customer": <message>}`. `final` has the reply as `result`. The `traces/` folder
is not committed. Section 4 and Lab 2 read these traces.

## What we fixed during the lab

1. Most smoke check runs of the first version were 10 of 10, but one run was 9 of 10: Emma's refund was promised but never prepared. Fix: one more line in the
   instructions ("When a refund is due, call prepare_refund before you answer").
2. Smoke check 9 of 10 again: Lukas (10 days before his trip) got a refund of 670, against the rules.
   Fix: the refund rules are now also written as code (`refund_amount` in `tools.py`), so `prepare_refund`
   returns an error with a hint when the amount is wrong. After that: 10 of 10, three runs in a row.
3. A blind spot: in one early run Tom got an invented change fee of 100 dollars (the policy says 30), but case 4
   only checked which tools were called. Fix: the change policy is now code too (`change_fee` in `tools.py`),
   and case 4 also checks the fee. Then: 10 of 10 again.
