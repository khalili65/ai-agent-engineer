# Session 4.2: Tracing and observability

Daniel wants to put the support agent into the chat on the Nova Travel website. Before that, he asks:
how long does a customer wait for an answer, and where does that time go?
Our JSON Lines trace from session 3.7 is a flat list with no clock times, so we give the agent **spans**,
written with the real **OpenTelemetry** SDK and named with the **OpenTelemetry GenAI semantic conventions**.

| File | What it does |
|---|---|
| `tools.py`, `data/` | A copy of the Lab 1 tools and data (the Lab 1 folder stays unchanged). |
| `otel_setup.py` | Creates the tracer. Every finished span is written as one JSON line to `traces/spans.jsonl` (and, with `--console`, also printed in full). |
| `traced_agent.py` | The Lab 1 OpenAI loop with three kinds of spans: `invoke_agent support agent` (the whole run), `chat gpt-4o-mini` (one model call) and `execute_tool <name>` (one tool call). |
| `show_tree.py` | Reads `traces/spans.jsonl` and prints one trace as a tree with a small timeline bar. |

```bash
uv run python sessions/4.2-tracing/traced_agent.py "Hi, Emma here. How many bags can I take on my Barcelona trip? My booking is NT-5582." --console
uv run python sessions/4.2-tracing/show_tree.py            # the last trace
uv run python sessions/4.2-tracing/show_tree.py a202fd     # one trace, by the start of its ID
```

## The span names and attributes we use

| Span | Name | Attributes |
|---|---|---|
| the whole run | `invoke_agent support agent` | `gen_ai.operation.name = invoke_agent`, `gen_ai.agent.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens` / `output_tokens` (sum of the run), plus our own `nova.customer_message` and `nova.reply` |
| one model call | `chat gpt-4o-mini` (kind `CLIENT`) | `gen_ai.operation.name = chat`, `gen_ai.provider.name = openai`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.response.id`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| one tool call | `execute_tool find_booking` | `gen_ai.operation.name = execute_tool`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, and the opt-in `gen_ai.tool.call.arguments` / `gen_ai.tool.call.result` |

The names come from the OpenTelemetry GenAI semantic conventions, which now live in their own repository:
https://github.com/open-telemetry/semantic-conventions-genai (`docs/gen-ai/client-inference.md`,
`gen-ai-spans.md`, `gen-ai-agent-spans.md`). Their status is **Development**, so names can still change:
check the repository before you copy them.

## Sending the same spans to a dashboard later

Langfuse and LangSmith can both receive OpenTelemetry spans (OTLP). To send these spans to one of them,
install `opentelemetry-exporter-otlp`, replace the file exporter in `otel_setup.py` with an
`OTLPSpanExporter`, and set the endpoint and key from that tool's docs. The agent code does not change.

`traces/spans.jsonl` holds the real spans from the video. Your own runs add new lines, and your numbers will differ.
