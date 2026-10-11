"""Session 3.1, step 3: the same job with native tool calling (the tools= parameter).

It prints what really travels: the request we send, the reply with tool_calls,
the tool message our code adds, and the final answer.
"""
import json
from text_protocol import client, MODEL, SARA, find_booking

# The tool description: name, what it does, and its input as a JSON schema
TOOLS = [{
    "type": "function",
    "function": {
        "name": "find_booking",
        "description": "Look up a Nova Travel booking by its booking ID.",
        "parameters": {
            "type": "object",
            "properties": {"booking_id": {"type": "string",
                                          "description": "Like NT-4821"}},
            "required": ["booking_id"],
        },
    },
}]

SYSTEM = ("You are the Nova Travel support agent. Check facts with your tools. "
          "Answer in two or three short sentences. "
          "You never send refunds yourself; a person approves every refund.")


def show(title, data):
    print(f"\n===== {title} =====")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": SARA}]

    # 1. Our request: the conversation plus the tool description
    request = {"model": MODEL, "messages": messages, "tools": TOOLS}
    show("1. Request we send", request)
    raw = client.chat.completions.with_raw_response.create(**request)

    # 2. The model's reply, exactly as the API sent it: no text, only a request
    show("2. Reply from the model", json.loads(raw.text)["choices"][0])
    reply = raw.parse().choices[0].message  # the same reply as a Python object
    messages.append(reply)  # keep the model's request in the conversation

    # 3. Our code runs the function and adds a message with the role "tool"
    for call in reply.tool_calls:
        args = json.loads(call.function.arguments)  # the arguments arrive as a JSON string
        result = find_booking(**args)
        tool_message = {"role": "tool", "tool_call_id": call.id,
                        "content": json.dumps(result)}
        messages.append(tool_message)
        show("3. Tool message our code adds", tool_message)

    # 4. Second call: now the model has the facts and writes the answer
    final = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
    print("\n===== 4. Final answer =====")
    print(final.choices[0].message.content)
