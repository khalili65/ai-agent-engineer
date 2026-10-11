"""Session 3.3, step 3: one reply from the model can hold several tool calls."""
import os
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, SYSTEM, MARIA

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

reply = client.chat.completions.create(
    model=MODEL, tools=TOOLS,
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": MARIA}],
).choices[0].message

print("Tool calls in this one reply:", len(reply.tool_calls or []))
for call in reply.tool_calls or []:
    print(f"  {call.id}  {call.function.name}  {call.function.arguments}")
