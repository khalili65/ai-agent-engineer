# Session 3.3: Many tools, parallel calls

Maria has two bookings with Nova Travel (NT-7012 Porto, NT-7013 Barcelona) and asks for her money back for both.
The support agent now has three tools: `find_booking`, `get_refund_rules` and `prepare_refund`
(`prepare_refund` only puts the request on Daniel's waiting list; a person approves every refund).

Run each file from the repository root, in this order:

| Step | File | What it shows |
|---|---|---|
| – | `nova_tools.py` | The bookings, the three tools, the tool descriptions, and the dispatch table `TOOL_FUNCTIONS` with `run_tool`. |
| 1 | `if_chain.py` | The old way: an if/elif chain. A tool name that is not in the chain silently returns `None`. |
| 2 | `dispatch_table.py` | A dictionary from tool name to function. An unknown name returns a clear error the model can read. |
| 3 | `two_bookings.py` | One reply from the model holds two tool calls (parallel tool calls), each with its own id. |
| 4 | `missing_answer.py` | Answer only one of the two calls: the API returns a 400 error and names the missing `tool_call_id`. |
| 5 | `agent.py` | The full agent loop with the dispatch table. Add `--one-at-a-time` to set `parallel_tool_calls=False`. |
| side trip | `async_basics/step1_sync.py` … `step5_blocking.py` | Async in Python with three pretend downloads (A 3 s, B 2 s, C 1 s): normal code takes 6 s; calling an `async def` function only makes a coroutine; `await` one by one is still 6 s; `asyncio.gather` takes 3 s and keeps the order; `time.sleep` inside async code blocks the event loop (6 s again). |
| 6 | `slow_tools.py` | The booking system needs 2 seconds per lookup (`asyncio.sleep`). One by one: 4 seconds. With `asyncio.gather`: 2 seconds. |
| 7 | `async_agent.py` | The agent with `AsyncOpenAI` and `asyncio.gather`: all tool calls of one reply run at the same time. |

```bash
uv run python sessions/3.3-many-tools/if_chain.py
uv run python sessions/3.3-many-tools/dispatch_table.py
uv run python sessions/3.3-many-tools/two_bookings.py
uv run python sessions/3.3-many-tools/missing_answer.py
uv run python sessions/3.3-many-tools/agent.py
uv run python sessions/3.3-many-tools/agent.py --one-at-a-time
uv run python sessions/3.3-many-tools/async_basics/step1_sync.py
uv run python sessions/3.3-many-tools/async_basics/step2_coroutine.py
uv run python sessions/3.3-many-tools/async_basics/step3_one_by_one.py
uv run python sessions/3.3-many-tools/async_basics/step4_gather.py
uv run python sessions/3.3-many-tools/async_basics/step5_blocking.py
uv run python sessions/3.3-many-tools/slow_tools.py
uv run python sessions/3.3-many-tools/async_agent.py
```

Notes
- `missing_answer.py` ends with a `BadRequestError` on purpose: every tool call id needs its own answer.
- The model's answers change from run to run. In our runs, the first reply always asked for both bookings at once,
  but `gpt-4o-mini` often got the 14-day rule wrong for the Porto trip (10 days before the trip means no refund).
  That is why a person approves every refund, and why section 4 is about catching mistakes like this.
- `asyncio.gather` returns the results in the same order as the calls, so each result goes back with the right id.
- Run tools at the same time only when they do not depend on each other. Read-only lookups are the safe case.
- Claude works the same way: several `tool_use` blocks in one reply, one `tool_result` for each, and
  `disable_parallel_tool_use: true` inside `tool_choice` to turn it off (see the Claude docs page "Parallel tool use").
