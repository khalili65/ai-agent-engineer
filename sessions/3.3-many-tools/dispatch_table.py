"""Session 3.3, step 2: the dispatch table, a dictionary from tool name to function."""
from nova_tools import TOOL_FUNCTIONS, run_tool

print("Tools in the table:", list(TOOL_FUNCTIONS))
print(run_tool("find_booking", {"booking_id": "NT-7012"}))
print(run_tool("get_refund_rules", {}))

# A tool the model knows about, but we forgot to put in the table:
print(run_tool("get_policy", {"topic": "pets"}))   # a clear error the model can read
TOOL_FUNCTIONS["get_policy"]                       # a plain lookup crashes the agent
