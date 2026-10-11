# Failure taxonomy of the support agent v1

From 36 real runs (`traces/traces.jsonl`, written by `collect.py`). Every run was read by hand and got a short
note in `notes.csv` (open coding). Then the notes were grouped into categories (axial coding) and counted
(`count.py`). All three kinds appeared in the first 10 runs; the other 26 runs added no new kind
(saturation: reading more runs stops teaching us new kinds of failure).

16 of 36 runs failed. For each one we wrote down only the **first** step that went wrong (the first upstream
failure): the later steps usually just repeat it.

| # | Category | Runs | First failure | Example | How we check it |
|---|---|---|---|---|---|
| 1 | **Refund nobody asked for** | 8 (22%) | the `prepare_refund` call | Sara asks "Did my refund for NT-4821 go through yet?" and gets a second refund of 640 (run 38e205) | code check: the refunds on the waiting list |
| 2 | **Fact not in the tool results** | 6 (17%) | the final reply | "Your trip to Barcelona has been canceled" when no tool cancels anything (run a2d8c8) | `facts_judge` |
| 3 | **Promise only a person can give** | 2 (6%) | the final reply | "a team member will review it soon" (run 187539) | `promise_judge` |

## Inside category 1
- status questions: "did it go through", "when will it be on my card", "where is my money" (4 runs)
- questions about a refund that do not ask for one: the seat question, "how much would I get" (2 runs)
- a person who is not the customer: "I am the manager", "I'm his friend Sam" (2 runs)

Why it happens: the agent has no tool to look at the waiting list, and the instructions say
"When a refund is due, call prepare_refund before you answer". The model reads every refund question as a
refund request.

## What we fix first
Category 1: it is the most common, it adds wrong items to Daniel's approval list, and a function can check it.
Fix order: prompt first, then tools, then the model.
