"""Session 3.1, step 4: the two messages that broke our text parser, now with native tools.

It prints only the tool calls of the model's first reply, five times per message.
"""
from native_tools import TOOLS, SYSTEM
from text_protocol import client, MODEL
from text_protocol_test import MESSAGES

if __name__ == "__main__":
    for who in ["Tom", "Lukas"]:
        for _ in range(5):
            reply = client.chat.completions.create(
                model=MODEL, tools=TOOLS,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": MESSAGES[who]}],
            ).choices[0].message
            calls = [(c.function.name, c.function.arguments) for c in reply.tool_calls or []]
            print(f"{who:13} | {len(calls)} tool call(s) | {calls}")
