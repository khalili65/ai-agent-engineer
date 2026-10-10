# AI Agent Engineer · course code

All the code for the **AI Agent Engineer** course: one folder per session that has code, and one folder per lab.
Our example company in every session is **Nova Travel**, a small online travel agency.

## What is in this repository

    ai-agent-engineer/
    ├── README.md            this file
    ├── pyproject.toml       the project: Python version and the packages we need
    ├── uv.lock              the exact package versions (uv writes it, you never edit it)
    ├── .python-version      the Python version uv uses
    ├── .env.example         an example settings file: copy it to .env and fill it in
    ├── .devcontainer/       settings for GitHub Codespaces (Python + uv, then `uv sync`)
    ├── src/nova/            the course check: `uv run nova check`
    ├── sessions/            code shown in the sessions (for example 1.3-first-agent)
    └── labs/                one folder per lab (for example 01-support-agent)

## Start in GitHub Codespaces (nothing to install)

1. Click the green **Code** button → **Codespaces** → **Create codespace on main**.
2. Wait until the editor opens. Codespaces runs `uv sync` for you.
3. In the terminal: `cp .env.example .env`, then open `.env` and fill in your provider.
4. Run `uv run nova check`.

## Start on your own computer

1. Install git and uv (see https://docs.astral.sh/uv/).
2. `git clone https://github.com/khalili65/ai-agent-engineer.git` and `cd ai-agent-engineer`
3. `uv sync` (uv installs the right Python and all packages into a `.venv` folder)
4. `cp .env.example .env`, fill it in, then `uv run nova check`.

## Choose a model provider (fill in ONE in `.env`)

| Provider | OPENAI_API_KEY | OPENAI_BASE_URL | MODEL |
|---|---|---|---|
| OpenAI (paid) | `sk-...` | *(keep the line commented out)* | `gpt-4o-mini` |
| OpenRouter (one key, many models, some free) | `sk-or-...` | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini`, or a free one such as `nvidia/nemotron-3-super-120b-a12b:free` |
| Ollama (free, on your computer) | `ollama` | `http://localhost:11434/v1` | `llama3.2:3b` |

Set a monthly spend limit in your provider's dashboard. Never share or commit your `.env` file.

Free models on OpenRouter are sometimes busy. If the check says "too many requests", wait a minute or pick another free model.
