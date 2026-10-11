"""Session 3.7: the support agent loop, with a trace line for every event."""
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from nova_data import FUNCTIONS, TOOLS
from trace_log import Trace

load_dotenv()  # reads OPENAI_API_KEY (and MODEL) from the .env file
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SYSTEM = ("You are the Nova Travel support agent. Check facts with your tools. "
          "Read the refund rules before you prepare a refund. You never send money: "
          "prepare_refund only puts a refund on a list, and a person approves it. "
          "Answer in two or three short sentences.")


def run_agent(message, trace, tools=TOOLS, max_steps=6):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": message}]
    for _ in range(max_steps):
        start = time.time()
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        reply = response.choices[0].message
        trace.log("model_call", name=MODEL,
                  args={"customer": message} if len(messages) == 2 else None,
                  result=response.choices[0].finish_reason,
                  input_tokens=response.usage.prompt_tokens,
                  output_tokens=response.usage.completion_tokens,
                  ms=round((time.time() - start) * 1000))
        messages.append(reply)
        if not reply.tool_calls:  # no request for a tool: this is the final answer
            trace.log("final", result=reply.content)
            return reply.content
        for call in reply.tool_calls:  # the model asks, our code runs the function
            args = json.loads(call.function.arguments)
            trace.log("tool_call", name=call.function.name, args=args)
            start = time.time()
            try:
                result = FUNCTIONS[call.function.name](**args)
                trace.log("tool_result", name=call.function.name, result=result,
                          ms=round((time.time() - start) * 1000))
            except Exception as e:
                result = {"error": str(e)}
                trace.log("error", name=call.function.name, result=str(e))
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    trace.log("error", name="max_steps", result=f"stopped after {max_steps} steps")
    return "Sorry, a person from our team will answer you soon."
