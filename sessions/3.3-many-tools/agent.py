"""Session 3.3, step 5: the support agent with three tools and a dispatch table."""
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, SYSTEM, MARIA, WAITING_LIST, run_tool

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_STEPS = 10

def run_agent(user_message, parallel=True):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}]
    tokens = 0
    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
            parallel_tool_calls=parallel,  # False: at most one tool call per reply
        )
        tokens += response.usage.total_tokens
        reply = response.choices[0].message
        messages.append(reply)
        if not reply.tool_calls:  # no tool call: this is the final answer
            print(f"Model call {step}: final answer ({tokens} tokens in total)")
            return reply.content
        print(f"Model call {step}: {len(reply.tool_calls)} tool call(s)")
        for call in reply.tool_calls:  # answer EVERY call, each with its own id
            args = json.loads(call.function.arguments)
            result = run_tool(call.function.name, args)
            print(f"  {call.function.name}({args}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return "Stopped: too many steps. A person takes over."

if __name__ == "__main__":
    parallel = "--one-at-a-time" not in sys.argv
    print("Agent:", run_agent(MARIA, parallel=parallel))
    print("Waiting list:", WAITING_LIST)
