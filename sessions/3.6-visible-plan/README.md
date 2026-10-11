# Session 3.6: A visible plan

Anna Weber sends Nova Travel one long message with four requests:
cancel the Barcelona trip (NT-5602), move the Vienna hotel one day later (NT-5603),
"what happens now?" about her mother Eva's cancelled flight to Rome (NT-5604),
and a question about bringing a small dog to Vienna.

The right result: two refunds and one date change on the waiting list (a person approves each one),
and an answer about the dog.
- NT-5602: changed mind, 40 days before the trip → $1,860 − $50 = **$1,810**
- NT-5603: new dates June 13 to June 16
- NT-5604: the airline cancelled → full refund **$720**

Run each file from the repository root:

| Step | File | What it shows |
|---|---|---|
| – | `support_tools.py` | The tools (`find_booking`, `get_refund_rules`, `get_policy`, `prepare_refund`, `change_booking`), the bookings, and Anna's message. Nothing here sends money. |
| 1 | `no_plan.py` | The agent without a plan. In our runs it often forgot Eva's refund and never read the refund rules. |
| 2 | `with_plan_v1.py` | First try with a plan tool. The plan comes before the facts, so the Eva item says "check the status", and the whole plan is ticked at once. |
| 3 | `with_plan.py` | The final version: look up the facts first, then write the plan; one tool call per step; `update_plan` answers with the next item; our code prints the plan live and does not let the agent stop while items are open. |

```bash
uv run python sessions/3.6-visible-plan/no_plan.py
uv run python sessions/3.6-visible-plan/with_plan_v1.py
uv run python sessions/3.6-visible-plan/with_plan.py
```

How the plan tool works
- `update_plan(items)` is a normal tool. The model always sends the **full list**; each item has a `task` and a `status` (`pending`, `in_progress`, `done`). It is a strict tool, so the status is always one of the three words.
- Our code keeps the list and prints it: `[ ]` pending, `[>]` in progress, `[x]` done.
- `parallel_tool_calls=False` asks for one tool call per step, so the plan can follow the work.
- Before the agent may give its final answer, our code checks that every item is done.

Notes
- Your runs will differ. In our five runs of `with_plan.py`, all three waiting-list items were there in four runs,
  and the Barcelona amount was right ($1,810) in three. A person still checks and approves every item.
- Coding agents use the same idea: Claude Code and the Claude Agent SDK ("Track todos": `TodoWrite` / Task tools),
  and LangChain Deep Agents (`write_todos`).
