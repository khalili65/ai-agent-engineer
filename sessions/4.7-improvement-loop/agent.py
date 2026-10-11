"""The support agent v1 from Lab 1, copied here so we can change one thing at a time.

Two things are settings now, so the eval can compare versions side by side:
the prompt (a file in prompts/) and the model.

    uv run python sessions/4.7-improvement-loop/agent.py "Hi, Sara again. Booking NT-4821. Did my refund go through yet?"
"""
import argparse
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import tools
from trace_log import TraceLog

load_dotenv()

PROMPTS = Path(__file__).parent / "prompts"
MAX_STEPS = 6            # model calls per run
TOKEN_BUDGET = 20000     # input + output tokens per run
HANDOFF = "Sorry, I could not finish this. A person from our team will write to you soon."


def ms_since(start):
    return round((time.time() - start) * 1000)


def run_tool(name, args, trace):
    """Run one tool. Problems come back as data, never as a crash."""
    trace.log("tool_call", name=name, args=args)
    start = time.time()
    if name not in tools.TOOLS:
        result = {"error": f"There is no tool called {name}.", "hint": f"Use one of: {', '.join(tools.TOOLS)}."}
        trace.log("error", name=name, result=result["error"])
        return result
    try:
        result = tools.TOOLS[name](**args)
    except Exception as e:
        trace.log("error", name=name, result=str(e))
        return {"error": f"{type(e).__name__}: {e}", "hint": "Check the arguments of the tool and try again."}
    trace.log("tool_result", name=name, result=result, ms=ms_since(start))
    return result


def run(message, model="gpt-4o-mini", prompt="v1", tool_names=None):
    """Answer one customer message with the chosen model and prompt. Returns the answer and the trace."""
    instructions = (PROMPTS / f"{prompt}.txt").read_text()
    specs = [s for s in tools.TOOL_SPECS if s["name"] in (tool_names or tools.V1_TOOLS)]
    trace = TraceLog()
    # The gpt-6 models accept function tools only on the Responses API (session 2.2).
    loop = run_responses if model.startswith("gpt-6") else run_chat
    answer = loop(message, model, instructions, specs, trace)
    trace.log("final", result=answer)
    return answer, trace


def run_chat(message, model, instructions, specs, trace):
    """The Lab 1 loop on Chat Completions."""
    client = OpenAI()
    tool_list = [{"type": "function", "function": s} for s in specs]
    messages = [{"role": "system", "content": instructions}, {"role": "user", "content": message}]
    used = 0
    for step in range(1, MAX_STEPS + 1):
        start = time.time()
        response = client.chat.completions.create(model=model, messages=messages, tools=tool_list)
        reply = response.choices[0].message
        used += response.usage.total_tokens
        trace.log("model_call", name=model, args={"customer": message} if step == 1 else None,
                  result=response.choices[0].finish_reason,
                  input_tokens=response.usage.prompt_tokens,
                  output_tokens=response.usage.completion_tokens, ms=ms_since(start))
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args, trace)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
        if used > TOKEN_BUDGET:
            break
    trace.log("error", name="limit", result=f"stopped after {step} steps, {used} tokens")
    return HANDOFF


def run_responses(message, model, instructions, specs, trace):
    """The same loop on the Responses API, for the gpt-6 models."""
    client = OpenAI()
    tool_list = [{"type": "function", **s} for s in specs]
    items = [{"role": "user", "content": message}]
    used = 0
    for step in range(1, MAX_STEPS + 1):
        start = time.time()
        response = client.responses.create(model=model, instructions=instructions, input=items,
                                           tools=tool_list, reasoning={"effort": "low"})
        calls = [item for item in response.output if item.type == "function_call"]
        used += response.usage.total_tokens
        trace.log("model_call", name=model, args={"customer": message} if step == 1 else None,
                  result="tool_calls" if calls else "stop",
                  input_tokens=response.usage.input_tokens,
                  output_tokens=response.usage.output_tokens, ms=ms_since(start))
        items += response.output
        if not calls:
            return response.output_text
        for call in calls:
            result = run_tool(call.name, json.loads(call.arguments or "{}"), trace)
            items.append({"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result)})
        if used > TOKEN_BUDGET:
            break
    trace.log("error", name="limit", result=f"stopped after {step} steps, {used} tokens")
    return HANDOFF


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    parser.add_argument("--model", default=os.getenv("MODEL", "gpt-4o-mini"))
    parser.add_argument("--prompt", default="v1")
    options = parser.parse_args()
    answer, trace = run(options.message, options.model, options.prompt)
    print("Agent:", answer)
    print("Waiting list:", tools.WAITING_LIST)
