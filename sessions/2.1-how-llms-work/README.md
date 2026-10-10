# Session 2.1: How LLMs work and how to choose one

Three small files. Run them from the repository root.

| File | What it shows | Cost |
|---|---|---|
| `tokens.py` | Sara's message cut into tokens (29 tokens for 21 words), with each token's number | free, no API call |
| `next_token.py` | the model's top 5 candidates for the next token, with their probabilities | far less than 1 cent |
| `cost_per_task.py` | the same task (answer Sara) on several models: tokens used and cost per task | about 1.5 cents for all four models, 3 runs each |

```bash
uv run python sessions/2.1-how-llms-work/tokens.py
uv run python sessions/2.1-how-llms-work/next_token.py
uv run python sessions/2.1-how-llms-work/cost_per_task.py
```

## Notes
- `tokens.py` uses `tiktoken`, the token library from OpenAI. It is already in the project (`uv sync` installs it).
- `next_token.py` needs a model that returns `logprobs` (for example `gpt-4o-mini` on OpenAI). Many other models and providers do not return them.
- `cost_per_task.py` uses OpenAI models by default. To test other models, give their names:
  `uv run python sessions/2.1-how-llms-work/cost_per_task.py gpt-4o-mini`.
  On OpenRouter or Ollama, set `OPENAI_BASE_URL` and the key in `.env` first. A model that is not in the `PRICES` list counts as free.
- **Prices change.** The `PRICES` list was copied from https://developers.openai.com/api/docs/pricing on 10 Oct 2026. Check the page and update the list before you trust the numbers.
- Some models think before they answer. Their hidden thinking tokens are paid as output tokens, so always compare the **cost per task**, not only the price per token.
