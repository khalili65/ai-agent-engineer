# Session 2.3: Structured outputs

Daniel's team wants every customer message turned into a clean ticket record that code can use:
booking ID, request type (refund, change or question), reason, and urgent yes or no.

Run each file from the repository root, in this order:

| Step | File | What it shows |
|---|---|---|
| 1 | `free_text.py` | Plain words are easy to read for a person, but `json.loads` fails on them. |
| 2 | `ask_for_json.py` | "Answer in JSON" in the prompt is not enough: the model often wraps the JSON in a code fence. It counts how many of 5 replies code can read. |
| – | `ticket.py` | The shape of one ticket as a Pydantic model. Run it to see the JSON schema that Pydantic makes. |
| 3 | `ticket_record.py` | Structured output: `client.chat.completions.parse(..., response_format=Ticket)` turns four messages into four valid `Ticket` objects. |
| 4 | `strict_tool.py` | A strict tool (`"strict": True`): the model asks for `request_refund` with arguments that always follow the schema. The tool only puts the request on Daniel's approval list; a person approves every refund. |
| 5 | `validate_retry.py` | Our own rule (`field_validator`): a booking ID is `NT-` and four digits, or null. If the ticket breaks the rule, the error goes back to the model, at most three tries. |

```bash
uv run python sessions/2.3-structured-outputs/free_text.py
uv run python sessions/2.3-structured-outputs/ask_for_json.py
uv run python sessions/2.3-structured-outputs/ticket.py
uv run python sessions/2.3-structured-outputs/ticket_record.py
uv run python sessions/2.3-structured-outputs/strict_tool.py
uv run python sessions/2.3-structured-outputs/validate_retry.py
```

Notes
- `free_text.py` ends with a `JSONDecodeError` on purpose: that is the problem this session solves.
- Strict tools need every field in `required` and `"additionalProperties": False`; without it the API answers with a 400 error.
- The same `Ticket` works with the Responses API: `client.responses.parse(model=MODEL, input=..., text_format=Ticket)` and then `response.output_parsed`.
- Claude has the same two ideas: JSON outputs (`client.messages.parse(..., output_format=Ticket)`) and strict tool use (`"strict": true`). See the Claude docs page "Structured outputs".
- Structured output needs a model that supports it (for example `gpt-4o-mini`). Some free or local models do not; then use `validate_retry.py` style checks.
- Your words will differ from the video: the shape stays the same, the `reason` text changes from run to run.
