# Session 3.5: Errors as data

Tools fail. A customer types a wrong booking number, or the booking system is slow or down.
In this session the support agent learns to handle those failures: the error becomes data
that goes back to the model, our code retries what is temporary, and a small loop detector
hands the customer to a person when the agent starts asking the same thing again.

`nova_system.py` is a small stand-in for the Nova Travel booking system, with the agent's
three tools: `find_booking`, `get_refund_rules` and `prepare_refund`. `prepare_refund` only
adds the refund to a waiting list ("waiting for a person to approve"). It never sends money.

Run each file from the repository root, in this order:

| Step | File | What it shows |
|---|---|---|
| 1 | `crash.py` | Emma writes `NT-512` (one digit is missing). `find_booking` raises a `KeyError`, and the whole agent crashes. |
| 2 | `catch_error.py` | The loop catches the error and sends the tool result `"Error"`. Nothing crashes, but the model has nothing to work with and gives Emma a wrong answer. |
| 3 | `clear_error.py` | The error message says what is wrong and what to do. The model asks Emma to check her number. Give more names to continue the chat: `emma emma2 emma3`. With `lukas`, the model repairs `6190` to `NT-6190` by itself. |
| 4 | `retry.py` | A temporary failure (a timeout) gets a retry from our code, with a short wait (1 s, then 2 s). Other errors go back to the model at once. Second argument: how many lookups time out (2 = slow, 99 = down). |
| 5 | `loop_guard.py` | A loop detector: the same tool call with the same arguments twice in one run means stop. The customer's message goes on the "for a person" list. |

```bash
uv run python sessions/3.5-errors-as-data/crash.py
uv run python sessions/3.5-errors-as-data/catch_error.py
uv run python sessions/3.5-errors-as-data/clear_error.py emma emma2 emma3
uv run python sessions/3.5-errors-as-data/clear_error.py lukas
uv run python sessions/3.5-errors-as-data/retry.py sara 2
uv run python sessions/3.5-errors-as-data/retry.py sara 99
uv run python sessions/3.5-errors-as-data/loop_guard.py sara
uv run python sessions/3.5-errors-as-data/loop_guard.py lukas 0
```

Notes
- `crash.py` ends with a traceback on purpose: that is the problem this session solves.
- Repair or retry? A bad input (a wrong booking number) goes back to the model with a clear
  message, so the model can fix it or ask the customer. A temporary problem (a timeout) is
  retried by our code, a few times, with a wait. If neither works, a person takes over.
- The loop detector compares the tool name and the arguments. A repaired call (`6190`, then
  `NT-6190`) has new arguments, so it is not a loop.
- Your replies will differ from the video. The model's words change from run to run.
- Section 13 goes deeper into retries (backoff, jitter, rate limits) and approvals.
