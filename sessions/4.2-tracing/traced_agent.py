"""The support agent v1 (OpenAI loop from Lab 1), now with OpenTelemetry spans.

    uv run python sessions/4.2-tracing/traced_agent.py "Hi, Emma here. ..."
    uv run python sessions/4.2-tracing/traced_agent.py "Hi, Emma here. ..." --console
"""
import argparse
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from opentelemetry.trace import SpanKind

from otel_setup import setup_tracing
from tools import TOOL_SPECS, TOOLS, WAITING_LIST

load_dotenv()
MAX_STEPS = 6
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


def run_tool(tracer, call):
    name = call.function.name
    args = json.loads(call.function.arguments or "{}")
    with tracer.start_as_current_span(f"execute_tool {name}") as span:  # child span: one tool
        span.set_attribute("gen_ai.operation.name", "execute_tool")
        span.set_attribute("gen_ai.tool.name", name)
        span.set_attribute("gen_ai.tool.call.id", call.id)
        span.set_attribute("gen_ai.tool.call.arguments", json.dumps(args))
        try:
            result = TOOLS[name](**args)
        except Exception as e:  # a wrong tool name or wrong arguments
            span.set_attribute("error.type", type(e).__name__)
            result = {"error": f"{type(e).__name__}: {e}", "hint": "Check the tool and its arguments."}
        span.set_attribute("gen_ai.tool.call.result", json.dumps(result))
        return result


def run(message, tracer):
    client = OpenAI()
    model = os.getenv("MODEL", "gpt-4o-mini")
    tools = [{"type": "function", "function": spec} for spec in TOOL_SPECS]
    messages = [{"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": message}]
    with tracer.start_as_current_span("invoke_agent support agent") as run_span:  # the whole run
        run_span.set_attribute("gen_ai.operation.name", "invoke_agent")
        run_span.set_attribute("gen_ai.agent.name", "support agent")
        run_span.set_attribute("gen_ai.provider.name", "openai")
        run_span.set_attribute("gen_ai.request.model", model)
        run_span.set_attribute("nova.customer_message", message)  # our own name, our own prefix
        tokens_in = tokens_out = 0
        for step in range(1, MAX_STEPS + 1):
            with tracer.start_as_current_span(f"chat {model}", kind=SpanKind.CLIENT) as span:
                span.set_attribute("gen_ai.operation.name", "chat")  # child span: one model call
                span.set_attribute("gen_ai.provider.name", "openai")
                span.set_attribute("gen_ai.request.model", model)
                response = client.chat.completions.create(model=model, messages=messages, tools=tools)
                span.set_attribute("gen_ai.response.model", response.model)
                span.set_attribute("gen_ai.response.id", response.id)
                span.set_attribute("gen_ai.response.finish_reasons", [response.choices[0].finish_reason])
                span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
                span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)
            tokens_in += response.usage.prompt_tokens
            tokens_out += response.usage.completion_tokens
            reply = response.choices[0].message
            messages.append(reply)
            if not reply.tool_calls:  # no tool requested: this is the final answer
                break
            for call in reply.tool_calls:
                result = run_tool(tracer, call)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
        run_span.set_attribute("gen_ai.usage.input_tokens", tokens_in)
        run_span.set_attribute("gen_ai.usage.output_tokens", tokens_out)
        run_span.set_attribute("nova.reply", reply.content or "")
        return reply.content, format(run_span.get_span_context().trace_id, "032x")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", default="Hi, this is Sara. The airline cancelled my "
                        "flight to Lisbon. My booking is NT-4821. Can I get my money back?")
    parser.add_argument("--console", action="store_true", help="also print every span in full")
    options = parser.parse_args()

    tracer = setup_tracing(show_in_terminal=options.console)
    answer, trace_id = run(options.message, tracer)
    print("Agent:", answer)
    print("Waiting list:", WAITING_LIST)
    print("Trace ID:", trace_id)
