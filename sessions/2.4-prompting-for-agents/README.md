# Session 2.4: Prompting for agents

Daniel does not like some answers of the support agent, so the team improves its system prompt.

| File | What it shows |
|---|---|
| `support_agent.py` | the agent loop from session 1.3, with the system prompt as an input |
| `altitude.py` | Sara's message with three system prompts: too low (brittle if-rules), too high (vague), and the right altitude |
| `few_shot.py` | the right prompt, without and with one example answer |
| `list_models.py` | which models your key can call (small GPT-5 models) |
| `effort.py` | a harder task (four refund requests, two of them close to the 14-day line) with reasoning effort none, low and high, three runs each |

Run them from the repository root:

    uv run python sessions/2.4-prompting-for-agents/altitude.py
    uv run python sessions/2.4-prompting-for-agents/few_shot.py
    uv run python sessions/2.4-prompting-for-agents/list_models.py
    uv run python sessions/2.4-prompting-for-agents/effort.py

`altitude.py` and `few_shot.py` use `MODEL` from your `.env` file (for example `gpt-4o-mini`).
`effort.py` needs a reasoning model that accepts `reasoning_effort`. It uses `gpt-5.6-luna` on OpenAI.
To try another one, set `REASONING_MODEL` in your `.env` file.

Your answers will use different words, because a model does not write the same text every time.
All four files together cost much less than one cent per run.
