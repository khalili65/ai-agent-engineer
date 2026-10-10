"""`uv run nova check`: checks that your computer is ready for the course."""
import os
import platform
import sys
from pathlib import Path

from dotenv import load_dotenv

OK, FAIL = "✓", "✗"


def fail(step: str, why: str, fix: str) -> int:
    print(f"{FAIL} {step}")
    print(f"   Problem: {why}")
    print(f"   Fix:     {fix}")
    return 1


def main() -> int:
    args = sys.argv[1:]
    if args[:1] != ["check"]:
        print("Usage: uv run nova check")
        return 2

    print("Nova Travel · course check\n")

    # 1. Python
    v = sys.version_info
    if v < (3, 11):
        return fail("Python", f"you have Python {v.major}.{v.minor}", "install Python 3.11 or newer")
    print(f"{OK} Python {platform.python_version()}")

    # 2. The .env settings file
    if not Path(".env").exists():
        return fail(".env file", "there is no .env file in this folder", "copy .env.example to .env and fill it in")
    load_dotenv(".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    if base_url is None:
        os.environ.pop("OPENAI_BASE_URL", None)  # an empty value would break the OpenAI library
    model = os.getenv("MODEL", "").strip()
    if not key:
        return fail("API key", "OPENAI_API_KEY is empty in your .env file", "paste your key after OPENAI_API_KEY=")
    print(f"{OK} API key found ({key[:3]}…)")
    if not model:
        return fail("Model", "MODEL is empty in your .env file", "write a model name after MODEL=")
    provider = "OpenAI" if not base_url else ("OpenRouter" if "openrouter" in base_url else ("Ollama" if "11434" in base_url else base_url))
    print(f"{OK} Provider: {provider} · model: {model}")

    # 3. One tiny request to the model
    from openai import OpenAI, APIError

    client = OpenAI(api_key=key, base_url=base_url)
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Greet Sara from Nova Travel in one short sentence."}],
            max_tokens=40,
        )
    except APIError as e:
        status = getattr(e, "status_code", None)
        if status == 401:
            return fail("Connection", "the provider did not accept your API key", "copy the key again from your provider's dashboard")
        if status == 404:
            return fail("Connection", f'model not found: "{model}"', "check the model name in your .env file")
        return fail("Connection", str(e)[:120], "check your internet connection and your .env settings")
    except Exception as e:  # network errors, Ollama not running, ...
        return fail("Connection", str(e)[:120], "check your internet connection (Ollama: is the Ollama app running?)")

    reply = (r.choices[0].message.content or "").strip()
    tokens = r.usage.total_tokens if r.usage else "?"
    print(f"{OK} Connection works\n")
    print(f"Model reply: {reply}")
    print(f"Tokens used: {tokens}\n")
    print("All checks passed. Your computer is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
