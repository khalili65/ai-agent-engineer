"""OpenTelemetry setup: every finished span is written as one JSON line to traces/spans.jsonl."""
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

SPANS_FILE = Path(__file__).parent / "traces" / "spans.jsonl"


def setup_tracing(show_in_terminal=False):
    SPANS_FILE.parent.mkdir(exist_ok=True)
    provider = TracerProvider(resource=Resource.create({"service.name": "nova-support-agent"}))
    # The exporter sends each span somewhere when it ends. Here: one JSON line in a file.
    to_file = ConsoleSpanExporter(out=open(SPANS_FILE, "a"),
                                  formatter=lambda span: span.to_json(indent=None) + "\n")
    provider.add_span_processor(SimpleSpanProcessor(to_file))
    if show_in_terminal:  # also print every span, in full, in the terminal
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    return trace.get_tracer("nova.support_agent")
