"""Session 3.2, step 1: one call to the model. What does the reply look like?"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from nova_tools import TOOLS, SYSTEM, SARA

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": SARA}]

response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
reply = response.choices[0].message

# Print the main parts of the reply, as the API returned them.
print(reply.model_dump_json(indent=2, include={"role", "content", "tool_calls"}))
print("finish_reason:", response.choices[0].finish_reason)
print("usage:", response.usage.prompt_tokens, "input tokens,",
      response.usage.completion_tokens, "output tokens")
