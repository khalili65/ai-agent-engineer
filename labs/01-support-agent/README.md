# Lab 1 · The support agent (no framework)

**Story:** Nova Travel's support agent helps Sara. Her flight to Lisbon was cancelled by the airline.
The agent finds her booking, reads the refund rules, prepares a refund, and waits for a person
to approve it (Daniel's rule).

## Files

| File | What it is |
|---|---|
| `agent.py` | the agent loop: the model decides, our code acts |
| `tools.py` | the tools the model may ask for (plain Python functions) |
| `data/bookings.json` | a small stand-in for the company booking system |
| `data/rules.md` | the company refund rules |
| `tests/test_tools.py` | quick tests for the tools (no model needed) |

## Run it

From the repository root:

    uv run python labs/01-support-agent/agent.py
    uv run pytest labs/01-support-agent

The agent uses the settings in your `.env` file (see `.env.example`).
