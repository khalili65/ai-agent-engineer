"""The support agent v1 from Lab 1 (an unchanged copy, so this session writes its own traces).

    uv run python sessions/4.6-trust-your-judge/agent_v1/agent.py "Hi, this is Sara ..."
"""
import argparse
import json
import os
import time

from dotenv import load_dotenv

from tools import TOOL_SPECS, TOOLS, WAITING_LIST
from trace_log import TraceLog

load_dotenv()

# Limits for one run, so the agent can never loop forever or spend too much.
MAX_STEPS = int(os.getenv("MAX_STEPS", "6"))            # model calls per run
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "20000"))  # input + output tokens per run
HANDOFF = "Sorry, I could not finish this. A person from our team will write to you soon."

INSTRUCTIONS = """You are the support agent of Nova Travel, a small online travel agency.
- Check every fact with your tools. Never guess a booking, a price or a rule.
- Before any refund, read the refund rules and work out the amount from the booking.
- When a refund is due, call prepare_refund before you answer.
  Never say that you will prepare it later.
- You never send money. prepare_refund only puts a refund on the waiting list,
  and a person on our team approves it. Tell the customer that.
- For questions about bags, changes or cancellations, read the policy.
- If a tool returns an error, follow its hint.
- Answer in two or three short sentences."""


def ms_since(start):
    return round((time.time() - start) * 1000)


def run_tool(name, args, trace):
    """Run one tool from the dispatch table. Problems come back as data, never as a crash."""
    trace.log("tool_call", name=name, args=args)
    start = time.time()
    if name not in TOOLS:
        result = {"error": f"There is no tool called {name}.", "hint": f"Use one of: {', '.join(TOOLS)}."}
        trace.log("error", name=name, result=result["error"])
        return result
    try:
        result = TOOLS[name](**args)
    except Exception as e:  # for example a missing or a wrong argument
        trace.log("error", name=name, result=str(e))
        return {"error": f"{type(e).__name__}: {e}", "hint": "Check the arguments of the tool and try again."}
    trace.log("tool_result", name=name, result=result, ms=ms_since(start))
    return result


def stop(trace, reason, detail):
    """A limit was hit: log it and hand the customer to a person."""
    trace.log("error", name=reason, result=detail)
    print(f"  stopped: {reason}")
    return HANDOFF


# ---------- The loop for OpenAI (Chat Completions) ----------
def run_openai(message, trace):
    from openai import OpenAI
    client = OpenAI()
    model = os.getenv("MODEL", "gpt-4o-mini")
    tools = [{"type": "function", "function": spec} for spec in TOOL_SPECS]
    messages = [{"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": message}]
    used = 0
    for step in range(1, MAX_STEPS + 1):
        start = time.time()
        response = client.chat.completions.create(model=model, messages=messages, tools=tools)
        reply = response.choices[0].message
        used += response.usage.total_tokens
        trace.log("model_call", name=model, args={"customer": message} if step == 1 else None,
                  result=response.choices[0].finish_reason,  # "tool_calls" or "stop"
                  input_tokens=response.usage.prompt_tokens,
                  output_tokens=response.usage.completion_tokens, ms=ms_since(start))
        messages.append(reply)
        if not reply.tool_calls:  # no tool requested: this is the final answer
            return reply.content
        for call in reply.tool_calls:  # one reply can ask for several tools at once
            args = json.loads(call.function.arguments or "{}")
            print(f"  step {step} · {call.function.name}({json.dumps(args)})")
            result = run_tool(call.function.name, args, trace)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
        if used > TOKEN_BUDGET:
            return stop(trace, "token_budget", f"used {used} tokens, budget {TOKEN_BUDGET}")
    return stop(trace, "max_steps", f"stopped after {MAX_STEPS} steps")


# ---------- The same loop for Claude (Messages API) ----------
def run_claude(message, trace):
    import anthropic
    client = anthropic.Anthropic()
    model = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")
    tools = [{"name": spec["name"], "description": spec["description"],
              "input_schema": spec["parameters"]} for spec in TOOL_SPECS]
    messages = [{"role": "user", "content": message}]
    used = 0
    for step in range(1, MAX_STEPS + 1):
        start = time.time()
        response = client.messages.create(model=model, max_tokens=4000, system=INSTRUCTIONS,
                                          tools=tools, messages=messages)
        used += response.usage.input_tokens + response.usage.output_tokens
        calls = [block for block in response.content if block.type == "tool_use"]
        text = " ".join(block.text for block in response.content if block.type == "text")
        trace.log("model_call", name=model, args={"customer": message} if step == 1 else None,
                  result="tool_calls" if calls else "stop",  # the same words as for OpenAI
                  input_tokens=response.usage.input_tokens,
                  output_tokens=response.usage.output_tokens, ms=ms_since(start))
        messages.append({"role": "assistant", "content": response.content})  # exactly as returned
        if not calls:
            return text
        results = []
        for call in calls:
            print(f"  step {step} · {call.name}({json.dumps(call.input)})")
            result = run_tool(call.name, call.input, trace)
            results.append({"type": "tool_result", "tool_use_id": call.id,
                            "content": json.dumps(result), "is_error": "error" in result})
        messages.append({"role": "user", "content": results})  # all results in one message
        if used > TOKEN_BUDGET:
            return stop(trace, "token_budget", f"used {used} tokens, budget {TOKEN_BUDGET}")
    return stop(trace, "max_steps", f"stopped after {MAX_STEPS} steps")


def run(message, provider="openai"):
    """Answer one customer message. Returns the answer and the trace of the run."""
    trace = TraceLog()
    loop = run_claude if provider == "claude" else run_openai
    answer = loop(message, trace)
    trace.log("final", result=answer)
    return answer, trace


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", default="Hi, this is Sara. The airline cancelled my "
                        "flight to Lisbon. My booking is NT-4821. Can I get my money back?")
    parser.add_argument("--provider", choices=["openai", "claude"], default="openai")
    options = parser.parse_args()

    print("Customer:", options.message)
    answer, trace = run(options.message, options.provider)
    print("Agent:", answer)
    print("Waiting list:", WAITING_LIST)
    print("Trace:", f"run {trace.run_id} in traces/{trace.path.name}")
