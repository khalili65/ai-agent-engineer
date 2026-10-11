# Session 3.2: The agent loop

The support agent now does the whole job for Sara: it finds her booking, reads the refund rules,
and prepares the refund. `prepare_refund` never sends money: it only puts the request on a waiting
list, and a person approves every refund (Daniel's rule).

Run each file from the repository root, in this order:

| Step | File | What it shows |
|---|---|---|
| – | `nova_tools.py` | The three tools (`find_booking`, `get_refund_rules`, `prepare_refund`), their descriptions, and the customer messages. |
| 1 | `one_step.py` | One model call. The reply has no text, only tool calls, each with its own ID. |
| 2 | `drop_message.py` | A common mistake: we skip the reply because it has no text. The API answers with a 400 error. |
| 3 | `agent_loop.py` | The full loop: append the reply exactly as returned, run the tools, append each result (the observation), and stop on a final answer, after `MAX_STEPS`, or when the token budget is used up. |
| 4 | `lost_number.py` | Emma lost her booking number. The model guesses numbers, and the loop stops after 6 steps. |
| 5 | `token_budget.py` | The same message with 20 steps allowed but a budget of 3,000 tokens. The budget stops it. |
| 6 | `sdk_runner.py` | The same agent with the OpenAI Agents SDK: `Runner.run_sync(agent, message, max_turns=6)` runs the loop for us. |

```bash
uv run python sessions/3.2-agent-loop/one_step.py
uv run python sessions/3.2-agent-loop/drop_message.py
uv run python sessions/3.2-agent-loop/agent_loop.py
uv run python sessions/3.2-agent-loop/lost_number.py
uv run python sessions/3.2-agent-loop/token_budget.py
uv run python sessions/3.2-agent-loop/sdk_runner.py
```

Notes
- `drop_message.py` ends with a `BadRequestError` (400) on purpose: "messages with role 'tool' must be a
  response to a preceeding message with 'tool_calls'". The fix is `messages.append(reply)` before the tool results.
- The model may ask for two tools in one reply (parallel tool calls). Session 3.3 looks at this closely.
- The budget is checked after each step, so the last step can go a little over the limit.
- Prices in `agent_loop.py` are for `gpt-4o-mini` ($0.15 input, $0.60 output per 1 million tokens).
  Check the OpenAI pricing page again: prices change.
- `sdk_runner.py` needs the `openai-agents` package (already in `pyproject.toml`). If you set no
  `max_turns`, the Agents SDK uses 10.
- Claude has a tool runner too: `client.beta.messages.tool_runner(...)` in the Anthropic Python SDK
  (beta). It loops until Claude answers without a tool call, or until `max_iterations`. See the Claude
  docs page "Tool runner (SDK)".
- Your words and guesses will differ from the video. The steps and the stops work the same way.
