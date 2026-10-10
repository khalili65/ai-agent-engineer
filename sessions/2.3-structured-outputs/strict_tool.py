"""Session 2.3, step 4: a strict tool. The model prepares a refund request; a person approves it."""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

APPROVAL_LIST = []  # Daniel's list: a person approves every refund

def request_refund(booking_id, reason, note):
    APPROVAL_LIST.append({"booking_id": booking_id, "reason": reason, "note": note,
                          "status": "waiting for a person"})
    return {"status": "waiting for a person to approve"}

TOOLS = [{"type": "function", "function": {
    "name": "request_refund",
    "description": "Put a refund request on Daniel's approval list. It never sends money.",
    "strict": True,  # the arguments always follow the schema below
    "parameters": {
        "type": "object",
        "properties": {
            "booking_id": {"type": "string", "description": "Like NT-4821."},
            "reason": {"type": "string", "enum": ["airline_cancelled", "changed_mind", "other"]},
            "note": {"type": "string", "description": "One short sentence for the person who approves."},
        },
        "required": ["booking_id", "reason", "note"],
        "additionalProperties": False,
    }}}]

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

reply = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are the Nova Travel support agent. "
         "For a refund, use the request_refund tool."},
        {"role": "user", "content": SARA},
    ],
    tools=TOOLS,
).choices[0].message

for call in reply.tool_calls or []:
    args = json.loads(call.function.arguments)  # strict: always valid, always complete
    print("Tool call:", call.function.name, args)
    print("Result:", request_refund(**args))
print("Approval list:", APPROVAL_LIST)
