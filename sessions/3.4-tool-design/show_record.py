"""Session 3.4: what the booking system returns for Sara, raw and short.

Run:  uv run python sessions/3.4-tool-design/show_record.py
"""
import json
import tiktoken
from nova import raw_record, short_record

encoding = tiktoken.get_encoding("o200k_base")  # the tokenizer of gpt-4o-mini
raw = json.dumps(raw_record("NT-4821"), indent=2)
short = json.dumps(short_record("NT-4821"), indent=2)
print(raw)
print(f"Raw record: {len(raw.splitlines())} lines, {len(encoding.encode(raw)):,} tokens\n")
print(short)
print(f"Short record: {len(short.splitlines())} lines, {len(encoding.encode(short)):,} tokens")
