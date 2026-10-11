"""Session 3.2: the agent loop, built piece by piece.

1. Call the model and append its reply exactly as returned.
2. Run every tool it asks for and append each result (the observation).
3. Stop on a final answer, after MAX_STEPS model calls, or when the token budget is used up.
"""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, FUNCTIONS, SYSTEM, SARA, WAITING_LIST

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

MAX_STEPS = 6          # at most 6 model calls for one customer message
MAX_TOKENS = 10_000    # token budget for one customer message
PRICE_IN, PRICE_OUT = 0.15, 0.60   # gpt-4o-mini, dollars per 1 million tokens


def run_agent(user_message, functions=FUNCTIONS, max_steps=MAX_STEPS, max_tokens=MAX_TOKENS):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}]
    tokens_in = tokens_out = 0

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        reply = response.choices[0].message
        messages.append(reply)                      # the reply, exactly as returned

        tokens_in += response.usage.prompt_tokens   # the real counts from the API
        tokens_out += response.usage.completion_tokens
        cost = tokens_in / 1_000_000 * PRICE_IN + tokens_out / 1_000_000 * PRICE_OUT
        print(f"Step {step}: {response.usage.prompt_tokens} input + "
              f"{response.usage.completion_tokens} output tokens | "
              f"budget {tokens_in + tokens_out:,} of {max_tokens:,} used, ${cost:.6f}")

        if not reply.tool_calls:                    # stop 1: the final answer
            print("Agent:", reply.content)
            return reply.content

        for call in reply.tool_calls:               # the model asks, our code acts
            args = json.loads(call.function.arguments)
            result = functions[call.function.name](**args)
            print(f"  tool: {call.function.name}({args})")
            print(f"  observation: {json.dumps(result)}")
            messages.append({"role": "tool", "tool_call_id": call.id,   # the observation
                             "content": json.dumps(result)})

        if tokens_in + tokens_out > max_tokens:     # stop 3: the budget is used up
            print(f"STOP: token budget of {max_tokens:,} used up. A person takes over.")
            return None

    print(f"STOP: {max_steps} steps and no final answer. A person takes over.")  # stop 2
    return None


if __name__ == "__main__":
    run_agent(SARA)
    print("Waiting list:", WAITING_LIST)
