# Session 3.1: Tool calling demystified

The model never runs a tool. It only writes a request; our code runs the function and sends
the result back. This folder builds that idea twice: first with a plain-text protocol and no
tools feature at all, then with native tool calling (the `tools=` parameter).

Run each file from the repository root, in this order:

| Step | File | What it shows |
|---|---|---|
| 1 | `text_protocol.py` | A system prompt asks the model to write `CALL find_booking <booking_id>`. Our code splits that line into three words, runs `find_booking`, and sends back a message that starts with `RESULT`. Works for Sara. |
| 2 | `text_protocol_test.py` | Four customer messages, five times each. The three-word parser fails when Tom writes `NT 5307` with a space, and when Lukas asks about two bookings (two `CALL` lines). |
| 3 | `native_tools.py` | The same job with `tools=`. It prints the request we send, the reply exactly as the API sent it (`tool_calls`, `id`, `function.name`, `function.arguments` as a JSON string, `finish_reason`), the `tool` message with `tool_call_id`, and the final answer. |
| 4 | `native_tools_test.py` | Tom and Lukas again, with native tools: Lukas's two bookings give two tool calls in one reply; the arguments are always valid JSON. |
| 5 | `missing_tool_message.py` | Forget the `tool` message and the API answers with a 400 error that names the missing `tool_call_id`. This file ends with that error on purpose. |

```bash
uv run python sessions/3.1-tool-calling/text_protocol.py
uv run python sessions/3.1-tool-calling/text_protocol.py "Hi, Tom again. My booking number is NT 5307. Can you move my Rome hotel two days later? Also, is breakfast included?"
uv run python sessions/3.1-tool-calling/text_protocol_test.py
uv run python sessions/3.1-tool-calling/native_tools.py
uv run python sessions/3.1-tool-calling/native_tools_test.py
uv run python sessions/3.1-tool-calling/missing_tool_message.py
```

Notes
- The second command (Tom's message) ends with `ValueError: too many values to unpack` on purpose: that is where the text protocol breaks.
- Your runs will differ a little. The `id` of a tool call is new every time, and the model sometimes writes `NT 5307` and sometimes `NT-5307`.
- Native tools fix the shape of a request, not its values: `"NT 5307"` is valid JSON but not a booking ID we know. Session 3.4 (tool design) and 3.5 (errors as data) handle that.
- All files use `gpt-4o-mini` by default (set `MODEL` in `.env` to change it). One run of every file together costs well under one cent.
