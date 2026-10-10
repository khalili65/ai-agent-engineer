# Session 2.2 · The APIs

Sara's question to the Nova Travel support agent, sent to a model in different ways.
Run every file from the repository root, for example:

    uv run python sessions/2.2-the-apis/chat_completions.py

| File | What it shows | Needs |
|---|---|---|
| `chat_completions.py` | The Chat Completions format: a list of `messages` in, `choices[0].message.content` out | any provider in `.env` (OpenAI, OpenRouter, Ollama) |
| `responses_api.py` | The OpenAI Responses API: `instructions` + `input` in, `output_text` out | an OpenAI key |
| `claude_messages.py` | The Claude Messages API: `system` + `messages` in, a list of content blocks out | an Anthropic key: add `ANTHROPIC_API_KEY=...` to `.env` (optional `CLAUDE_MODEL=...`) |
| `streaming.py` | `stream=True`: the words arrive piece by piece, with the timing printed at the end | any provider in `.env` |
| `image_input.py` | Image input: the model reads `flight_notice.png` (an example image made for the course) | a model that accepts images, e.g. `gpt-4o-mini` |

## The same code, another provider

`chat_completions.py` works with every provider that offers the Chat Completions format.
Only three settings change, in `.env` or in the terminal:

    OPENAI_BASE_URL=https://openrouter.ai/api/v1
    OPENAI_API_KEY=sk-or-...
    MODEL=nvidia/nemotron-3-super-120b-a12b:free

Free models are sometimes busy. If you see "too many requests", wait a minute or pick another free model.

## Cost

With `gpt-4o-mini` each text run costs a small fraction of a cent. The image run uses about 25,000 input tokens
(images count as many tokens) and still costs less than half a cent.
