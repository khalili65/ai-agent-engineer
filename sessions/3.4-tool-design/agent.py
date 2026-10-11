"""Session 3.4: one agent loop that works with any tool set, and writes a JSONL trace."""
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_STEPS = 6
TRACES = Path(__file__).parent / "traces"

SYSTEM = ("You are the Nova Travel support agent. Check facts with your tools. "
          "Read the refund rules before you decide about a refund. "
          "If the customer asks for a refund and the rules allow it, prepare it right away. "
          "You never send money; a person approves every refund. "
          "Answer in short, simple sentences.")


def run_agent(user_message, tools, functions, run_id, trace_file):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}]
    calls, input_tokens, output_tokens = [], 0, 0
    TRACES.mkdir(exist_ok=True)
    with open(TRACES / trace_file, "a") as trace:
        def log(**row):
            trace.write(json.dumps({"run_id": run_id, **row}) + "\n")
        for step in range(1, MAX_STEPS + 1):
            start = time.perf_counter()
            response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
            reply = response.choices[0].message
            input_tokens += response.usage.prompt_tokens
            output_tokens += response.usage.completion_tokens
            log(step=step, type="model_call", name=MODEL, args=None, result=None,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                ms=round((time.perf_counter() - start) * 1000))
            messages.append(reply)
            if not reply.tool_calls:
                log(step=step, type="final", name=None, args=None, result=reply.content,
                    input_tokens=0, output_tokens=0, ms=0)
                return {"calls": calls, "answer": reply.content,
                        "input_tokens": input_tokens, "output_tokens": output_tokens}
            for call in reply.tool_calls:
                args = json.loads(call.function.arguments)
                function = functions.get(call.function.name)
                try:
                    result = function(**args) if function else {"error": "unknown tool"}
                except TypeError as error:  # missing or unknown argument
                    result = {"error": str(error)}
                calls.append({"name": call.function.name, "args": args, "result": result})
                log(step=step, type="tool_call", name=call.function.name, args=args,
                    result=result, input_tokens=0, output_tokens=0, ms=0)
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result)})
    return {"calls": calls, "answer": "Stopped: too many steps.",
            "input_tokens": input_tokens, "output_tokens": output_tokens}
