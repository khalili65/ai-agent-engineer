"""Session 3.4: print exactly what the model reads for one tool, in version 1 or version 2.

Run:  uv run python sessions/3.4-tool-design/show_tools.py v1 get_booking_price
      uv run python sessions/3.4-tool-design/show_tools.py v2 find_booking
"""
import json
import sys
import tools_v1
import tools_v2

version = sys.argv[1] if len(sys.argv) > 1 else "v1"
name = sys.argv[2] if len(sys.argv) > 2 else "get_booking_price"
tools = tools_v1.TOOLS if version == "v1" else tools_v2.TOOLS
for tool in tools:
    if tool["function"]["name"] == name:
        print(json.dumps(tool, indent=2))
