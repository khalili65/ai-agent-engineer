# Session 1.4 · What an agent really is

One job for Nova Travel, solved three ways: answer Sara (booking NT-4821, the airline cancelled her flight),
tell her how much money she gets back, and prepare the refund so that **a person approves it** (Daniel's rule).

| File | What it is |
|---|---|
| `llm_call.py` | way 1: one LLM call. No tools, no steps. It cannot see the booking. |
| `workflow.py` | way 2: a workflow. Our code decides four fixed steps; the model only writes the reply. |
| `agent.py` | way 3: an agent. The model chooses the next step in a loop; our code runs the tools. |
| `refund_rule.py` | the refund rule as a plain Python function (no AI) |
| `ask_the_model.py` | the same rule asked of the model 10 times, to compare with the function |
| `nova_office.py` | the plain Python part of Nova Travel: bookings, `find_booking`, `prepare_refund` (never sends money) |

## Run it

From the repository root:

    uv run python sessions/1.4-what-an-agent-is/llm_call.py
    uv run python sessions/1.4-what-an-agent-is/workflow.py
    uv run python sessions/1.4-what-an-agent-is/agent.py
    uv run python sessions/1.4-what-an-agent-is/refund_rule.py
    uv run python sessions/1.4-what-an-agent-is/ask_the_model.py        # Omar, 14 days before the trip
    uv run python sessions/1.4-what-an-agent-is/ask_the_model.py 30     # Omar, 30 days before the trip

`workflow.py` and `agent.py` also take another message, for example:

    uv run python sessions/1.4-what-an-agent-is/agent.py "Hi, this is Sara again. How many nights is my Lisbon trip? My booking is NT-4821."

The model's words change from run to run. The facts come from the booking and the refund rule, so they stay the same.

## The rule of this session

**If a function can do it, write the function.** Use the model for the parts that need language
(reading what a customer wants, writing a kind reply), and use the least autonomy that does the job:

    one LLM call  →  workflow (our code decides the steps)  →  agent (the model decides the steps)

## Glossary (one word, one meaning, for the whole course)

| Term | Meaning |
|---|---|
| LLM | a large language model: the AI model that reads text and writes text |
| agent | an LLM choosing its next action in a loop |
| workflow | steps decided in code |
| tool / tool call / observation | a function the model may request / the request / the result returned (in 1.3 we said "tool result") |
| step | one model call in the loop |
| state | data your code owns during a run (here: the list of refunds waiting for approval) |
| memory | data kept across runs |
| context | everything sent to the model in one call |
| knowledge base | documents searched with retrieval |
| eval / trace | a repeatable measurement on fixed cases / the recorded steps of one run |
| grader / judge | anything that scores an output / an LLM used as a grader |
| simulated user | an LLM playing the customer in a multi-turn eval |
| end-state check | checking the database after a run, not the words |
| guardrail / approval gate | an automatic check / a human must confirm an action |
| handoff | one agent passing control to another |
| harness | the code around the model loop: tools, context, memory, permissions, verification |
| skill | a folder of instructions and scripts loaded on demand (SKILL.md) |
| LLM gateway | a proxy in front of model providers: routing, failover, budgets |
| MCP gateway | a proxy in front of MCP servers: auth, policy, audit |
