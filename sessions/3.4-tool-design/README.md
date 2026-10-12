# Session 3.4: Tool design

The support agent has tools that work, but it picks the wrong one or fills the arguments badly.
This folder compares two versions of the same tools on six real customer messages, five runs each,
and then compares a big raw tool answer with a short one.

| File | What it is |
|---|---|
| `booking_system.json` | A local stand-in for Nova Travel's booking system: big raw records (prices in cents, status codes, audit log). |
| `nova.py` | Loads the records; `raw_record()` returns everything, `short_record()` only what the agent needs. Refund rules and Daniel's waiting list. |
| `tools_v1.py` | Tools made in a hurry: vague names (`get_data`, `rules`, `refund`), no descriptions, every argument loose text, three overlapping price/city/dates tools. |
| `tools_v2.py` | Three designed tools: `find_booking`, `get_refund_rules`, `prepare_refund`. Clear names, descriptions that say when to use each tool, strict schemas (`pattern`, `number`, `enum`). |
| `agent.py` | One agent loop for any tool set. Writes a JSONL trace to `traces/`. |
| `test_tools.py` | Runs the six messages five times and counts right results, wrong tool calls and argument errors. |
| `show_tools.py` | Prints exactly what the model reads for one tool (`v1 get_booking_price`, `v2 find_booking`). |
| `show_trace.py` | Prints one run of a test, step by step, from its trace file: each tool call, what the tool sent back, and the answer. |
| `show_record.py` | Prints Sara's raw record and her short record, with token counts. |
| `response_size.py` | Same tools v2, but `find_booking` returns the raw record (`detailed`) or the short one (`concise`). |

```bash
uv run python sessions/3.4-tool-design/test_tools.py v1
uv run python sessions/3.4-tool-design/test_tools.py v2
uv run python sessions/3.4-tool-design/show_tools.py v1 get_booking_price
uv run python sessions/3.4-tool-design/show_trace.py test_v1.jsonl "v1-Sara: flight-4"
uv run python sessions/3.4-tool-design/show_record.py
uv run python sessions/3.4-tool-design/response_size.py detailed
uv run python sessions/3.4-tool-design/response_size.py concise
```

Notes
- `test_tools.py` and `response_size.py` call the model many times (about 60 and 40 conversations
  with `gpt-4o-mini`; together well under 5 cents).
- A refund counts as right only if the request on Daniel's list has the right booking ID and the
  amount is a number with the right value (330 for John, 640 for Sara). `"640.00"` as text counts as
  an argument error: the code cannot know if a text like `"64000"` means dollars or cents.
- Version 2 changes several things at once (names, descriptions, schemas, fewer tools, short answers).
  `response_size.py` changes only one thing: the size of the tool answer.
- Your numbers will differ a little from the video: real runs vary.
- No tool sends money. Even `refund` in version 1 only adds to the waiting list; a person approves every refund.
