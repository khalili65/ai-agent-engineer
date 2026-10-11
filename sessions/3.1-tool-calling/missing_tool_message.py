"""Session 3.1, step 5: what if our code forgets the tool message?

The model asked for find_booking, but we send the conversation back without a
message with the role "tool" for that tool_call_id. The API refuses the request.
"""
from native_tools import TOOLS, SYSTEM
from text_protocol import client, MODEL, SARA

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": SARA}]
reply = client.chat.completions.create(
    model=MODEL, messages=messages, tools=TOOLS).choices[0].message
messages.append(reply)
print("The model asked for:", reply.tool_calls[0].function.name, reply.tool_calls[0].id)

# We "forget" to add the tool message and call the model again
client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
